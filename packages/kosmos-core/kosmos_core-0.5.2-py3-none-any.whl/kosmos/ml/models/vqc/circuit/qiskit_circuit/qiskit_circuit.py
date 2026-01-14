import numpy as np
import torch
from qiskit import ClassicalRegister, QuantumCircuit

from kosmos.circuit_runner.qiskit_runner import QiskitRunner
from kosmos.ml.models.vqc.circuit.circuit import ParameterizedCircuit
from kosmos.ml.models.vqc.circuit.qiskit_circuit.autograd_function import QiskitAutogradFunction
from kosmos.ml.models.vqc.encoding.encoding import VQCEncoding
from kosmos.ml.typing import TensorMapping, TensorNpArray


class QiskitParameterizedCircuit(ParameterizedCircuit):
    """Parameterized quantum circuit using Qiskit."""

    def __init__(  # noqa: PLR0913
        self,
        circuit_runner: QiskitRunner,
        encoding: VQCEncoding,
        num_layers: int,
        weight_mapping_func: TensorMapping | None,
        input_mapping_func: TensorMapping | None,
        output_scaling_parameter: torch.Tensor | None,
        bias_parameter: torch.Tensor | None,
        *,
        data_reuploading: bool,
    ) -> None:
        """Initialize the circuit.

        Args:
            circuit_runner (QiskitRunner): The Qiskit circuit runner.
            encoding (VQCEncoding): The VQC encoding.
            num_layers (int): The number of variational layers.
            weight_mapping_func (TensorMapping | None): The mapping function for the weights.
            input_mapping_func (TensorMapping | None): The mapping function for the inputs.
            output_scaling_parameter (torch.Tensor | None): The output scaling parameter.
            bias_parameter (torch.Tensor | None): The bias parameter.
            data_reuploading (bool): Whether to use data re-uploading.

        """
        super().__init__(
            circuit_runner,
            encoding,
            num_layers,
            weight_mapping_func,
            input_mapping_func,
            output_scaling_parameter,
            bias_parameter,
            data_reuploading=data_reuploading,
        )
        self.circuit_runner = circuit_runner
        self.gradient_method = self.circuit_runner.get_gradient_method(self)

    def circuit(self, weights: TensorNpArray, x: TensorNpArray) -> QuantumCircuit:
        """Circuit definition.

        Args:
            weights (TensorNpArray): Weights values.
            x (TensorNpArray): Input values.

        Returns:
            QuantumCircuit: The quantum circuit.

        """
        qc = QuantumCircuit(self.num_qubits)

        if not self.data_reuploading:
            self.encoding.apply_operation(x, wires=range(self.num_qubits), qc=qc)

        for w in weights:
            if self.data_reuploading:
                self.encoding.apply_operation(x, wires=range(self.num_qubits), qc=qc)
            for q in range(self.num_qubits):
                qc.rz(float(w[q, 0]), q)
                qc.ry(float(w[q, 1]), q)
                qc.rz(float(w[q, 2]), q)

            if self.num_qubits > 1:
                for q in range(self.num_qubits):
                    qc.cx(q, (q + 1) % self.num_qubits)

        classical_reg = ClassicalRegister(self.output_dim, "c")
        qc.add_register(classical_reg)
        qc.measure(range(self.output_dim), range(self.output_dim))

        return qc

    def execute_circuits(self, qcs: list[QuantumCircuit]) -> list[np.ndarray]:
        """Execute given circuits and calculate Z expectation values.

        Args:
            qcs (list[QuantumCircuit]): List of quantum circuits.

        Returns:
            list[np.ndarray]: Z expectation values.

        """
        return self.circuit_runner.expectation_values(qcs)

    def execute(self, x: TensorNpArray, weights: np.ndarray) -> torch.Tensor:
        """Create circuits, execute circuits, and calculate Z expectation values.

        Args:
            x (TensorNpArray): Input values.
            weights (np.ndarray): Weights values.

        Returns:
            torch.Tensor: Output tensor.

        """
        x = x.detach().cpu().numpy() if isinstance(x, torch.Tensor) else x
        qcs = [self.circuit(weights, model_input) for model_input in x]
        outputs = self.execute_circuits(qcs)
        return torch.from_numpy(np.stack(outputs)).float()

    def forward_circuit(self, x: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
        """Compute model outputs for inputs and weights.

        Args:
            x (torch.Tensor): Input tensor.
            weights (torch.Tensor): Weights tensor.

        Returns:
            torch.Tensor: Output tensor.

        """
        mapped_weights = self.weight_mapping_func(weights)
        mapped_inputs = self.input_mapping_func(x)

        output = QiskitAutogradFunction.apply(
            mapped_inputs, mapped_weights, self.execute, self.gradient_method.jacobian
        )

        if self.output_scaling_parameter is not None:
            output = self.output_scaling_parameter * output

        if self.bias_parameter is not None:
            output = output + self.bias_parameter

        return output
