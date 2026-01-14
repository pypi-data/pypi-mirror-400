from abc import ABC, abstractmethod

import torch

from kosmos.circuit_runner.circuit_runner import CircuitRunner
from kosmos.ml.models.vqc.encoding.encoding import VQCEncoding
from kosmos.ml.typing import TensorMapping


class ParameterizedCircuit(ABC):
    """Abstract base class for parameterized quantum circuits."""

    def __init__(  # noqa: PLR0913
        self,
        circuit_runner: CircuitRunner,
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
            circuit_runner (CircuitRunner): The quantum circuit runner.
            encoding (VQCEncoding): The VQC encoding.
            num_layers (int): The number of variational layers.
            weight_mapping_func (TensorMapping | None): The mapping function for the weights.
            input_mapping_func (TensorMapping | None): The mapping function for the inputs.
            output_scaling_parameter (torch.Tensor | None): The output scaling parameter.
            bias_parameter (torch.Tensor | None): The bias parameter.
            data_reuploading (bool): Whether to use data re-uploading.

        """
        self.circuit_runner = circuit_runner
        self.encoding = encoding
        self.num_qubits = self.encoding.num_qubits
        self.input_dim = self.encoding.input_dim
        self.output_dim = self.encoding.output_dim

        self.num_layers = num_layers
        self.weight_mapping_func = weight_mapping_func
        self.input_mapping_func = input_mapping_func
        self.output_scaling_parameter = output_scaling_parameter
        self.bias_parameter = bias_parameter
        self.data_reuploading = data_reuploading

    @abstractmethod
    def forward_circuit(self, x: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
        """Compute model outputs for inputs and weights.

        Args:
            x (torch.Tensor): Input tensor.
            weights (torch.Tensor): Weights tensor.

        Returns:
            torch.Tensor: Output tensor.

        """
