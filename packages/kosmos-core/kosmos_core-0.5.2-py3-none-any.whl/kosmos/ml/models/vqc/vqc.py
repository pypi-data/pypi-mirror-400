import torch
from torch import nn

from kosmos.circuit_runner.circuit_runner import CircuitRunner
from kosmos.ml.config.factories.encoding import EncodingConfig
from kosmos.ml.models.model import Model
from kosmos.ml.models.vqc.circuit.circuit import ParameterizedCircuit
from kosmos.ml.models.vqc.circuit.pennylane_circuit import PennyLaneParameterizedCircuit
from kosmos.ml.models.vqc.circuit.qiskit_circuit.qiskit_circuit import QiskitParameterizedCircuit
from kosmos.ml.typing import TensorMapping


class VQC(Model):
    """Variational quantum circuit."""

    def __init__(  # noqa: PLR0913
        self,
        circuit_runner: CircuitRunner,
        input_dim: int,
        output_dim: int,
        num_layers: int,
        encoding_config: EncodingConfig,
        weight_mapping_func: TensorMapping | None,
        input_mapping_func: TensorMapping | None,
        weight_init_range: tuple[float, float],
        bias_init_range: tuple[float, float] | None,
        *,
        data_reuploading: bool,
        output_scaling: bool,
    ) -> None:
        """Initialize the VQC.

        Args:
            circuit_runner (CircuitRunner): The quantum circuit runner to use for the quantum
                circuit.
            input_dim (int): The input dimension of the model.
            output_dim (int): The output dimension of the model.
            num_layers (int): The number of variational layers.
            encoding_config (EncodingConfig): The encoding configuration.
            weight_mapping_func (TensorMapping | None): The mapping function for the weights.
            input_mapping_func (TensorMapping | None): The mapping function for the input.
            weight_init_range (tuple[float, float]): Lower and upper bounds for initializing the
                trainable weight parameters.
            bias_init_range (tuple[float, float] | None): Lower and upper bounds for initializing
                the trainable bias parameters applied to each output unit. If None, no bias
                parameters are used.
            data_reuploading (bool): Whether to use data re-uploading.
            output_scaling (bool): Whether to use output scaling.

        """
        super().__init__(input_dim, output_dim)

        self.circuit_runner = circuit_runner

        self.num_layers = num_layers
        self.weight_mapping_func = weight_mapping_func or (lambda x: x)
        self.input_mapping_func = input_mapping_func or (lambda x: x)

        self.data_reuploading = data_reuploading
        self.output_scaling = output_scaling

        if encoding_config.framework is None:
            encoding_config.framework = self.circuit_runner.framework
        self.encoding = encoding_config.get_instance(self.input_dim, self.output_dim)

        self.num_qubits = self.encoding.num_qubits

        # Trainable parameters
        init_min, init_max = weight_init_range
        self.weights = nn.Parameter(
            torch.empty(self.num_layers, self.num_qubits, 3, dtype=torch.float32).uniform_(
                init_min, init_max
            )
        )

        if bias_init_range is not None:
            init_min, init_max = bias_init_range
            self.bias = nn.Parameter(
                torch.empty(self.output_dim, dtype=torch.float32).uniform_(init_min, init_max)
            )
        else:
            self.bias = None

        self.output_scaling_parameter = (
            nn.Parameter(torch.ones(1, dtype=torch.float32)) if self.output_scaling else None
        )

        circuit_implementations: dict[str, type[ParameterizedCircuit]] = {
            "pennylane": PennyLaneParameterizedCircuit,
            "qiskit": QiskitParameterizedCircuit,
        }
        cls = circuit_implementations[self.circuit_runner.framework]
        self.circuit = cls(
            self.circuit_runner,
            self.encoding,
            self.num_layers,
            self.weight_mapping_func,
            self.input_mapping_func,
            self.output_scaling_parameter,
            self.bias,
            data_reuploading=self.data_reuploading,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Perform a forward pass.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor.

        """
        return self.circuit.forward_circuit(x, self.weights)
