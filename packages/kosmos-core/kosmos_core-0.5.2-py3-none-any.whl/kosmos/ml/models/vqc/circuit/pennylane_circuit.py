import pennylane as qml
import torch
from pennylane.measurements import ExpectationMP

from kosmos.circuit_runner.pennylane_runner import PennyLaneRunner
from kosmos.ml.models.vqc.circuit.circuit import ParameterizedCircuit
from kosmos.ml.models.vqc.encoding.encoding import VQCEncoding
from kosmos.ml.typing import TensorMapping


class PennyLaneParameterizedCircuit(ParameterizedCircuit):
    """Parameterized quantum circuit using PennyLane."""

    def __init__(  # noqa: PLR0913
        self,
        circuit_runner: PennyLaneRunner,
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
            circuit_runner (PennyLaneRunner): The PennyLane circuit runner.
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
        self.circuit_runner.configure_qnode(self.num_qubits, self._circuit)

    def _circuit(self, weights: torch.Tensor, x: torch.Tensor) -> list[ExpectationMP]:
        """Circuit definition.

        Args:
            weights (torch.Tensor): Weights tensor.
            x (torch.Tensor): Input tensor.

        Returns:
            list[ExpectationMP]: List of Z-expectation measurement processes.

        """
        if not self.data_reuploading:
            self.encoding.apply_operation(x, wires=range(self.num_qubits))

        for w in weights:
            if self.data_reuploading:
                self.encoding.apply_operation(x, wires=range(self.num_qubits))
            qml.StronglyEntanglingLayers(w.unsqueeze(0), wires=range(self.num_qubits))

        return [qml.expval(qml.PauliZ(i)) for i in range(self.output_dim)]

    def expect_z(self, weights: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """Execute the circuit and calculate Z expectation values.

        Args:
            weights (torch.Tensor): Weights tensor.
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Z expectation values.

        """
        return qml.math.stack(self.circuit_runner.execute(weights, x))

    def forward_circuit(self, x: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
        """Compute model outputs for inputs and weights.

        Args:
            x (torch.Tensor): Input tensor.
            weights (torch.Tensor): Weights tensor.

        Returns:
            torch.Tensor: Output tensor.

        """
        outputs = []

        mapped_weights = self.weight_mapping_func(weights)

        for model_input in x:
            mapped_input = self.input_mapping_func(model_input)
            circuit_out = self.expect_z(mapped_weights, mapped_input)
            outputs.append(circuit_out.to(torch.float32))

        output = torch.stack(outputs)

        if self.output_scaling_parameter is not None:
            output = self.output_scaling_parameter * output

        if self.bias_parameter is not None:
            output = output + self.bias_parameter

        return output
