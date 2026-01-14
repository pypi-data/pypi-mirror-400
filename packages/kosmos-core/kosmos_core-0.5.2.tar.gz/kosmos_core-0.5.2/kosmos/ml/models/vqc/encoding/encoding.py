import math
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Literal

from qiskit import QuantumCircuit
from torch import Tensor

from kosmos.circuit_runner.typing import QuantumCircuitFramework


class VQCEncoding(ABC):
    """Feature encoding for the VQC."""

    def __init__(self, input_dim: int, output_dim: int) -> None:
        """Initialize the encoding.

        Args:
            input_dim (int): The input dimension of the model.
            output_dim (int): The output dimension of the model.

        """
        self.input_dim = input_dim
        self.output_dim = output_dim

    @property
    @abstractmethod
    def num_qubits(self) -> int:
        """Number of required qubits."""

    @property
    @abstractmethod
    def framework(self) -> QuantumCircuitFramework:
        """The framework used for the quantum circuit."""

    @abstractmethod
    def apply_operation(
        self, features: Tensor, wires: Sequence[int], qc: QuantumCircuit | None = None
    ) -> None:
        """Apply the operation for encoding.

        Args:
            features (Tensor): Input features.
            wires (Sequence[int]): Target wires.
            qc (QuantumCircuit | None): The quantum circuit to use for the encoding
                (only for 'qiskit' framework).

        """
        if self.framework == "qiskit" and qc is None:
            msg = "Quantum circuit is required for 'qiskit' framework."
            raise ValueError(msg)
        if self.framework != "qiskit" and qc is not None:
            msg = "Quantum circuit should be None for non-'qiskit' framework."
            raise ValueError(msg)


class AngleEmbedding(VQCEncoding, ABC):
    """Abstract base for angle embedding."""

    def __init__(self, input_dim: int, output_dim: int, rotation: Literal["X", "Y", "Z"]) -> None:
        """Initialize the angle embedding.

        Args:
            input_dim (int): The input dimension of the model.
            output_dim (int): The output dimension of the model.
            rotation (Literal["X", "Y", "Z"]): The rotation to use for the angle embedding.

        """
        super().__init__(input_dim, output_dim)
        self.rotation = rotation

    @property
    def num_qubits(self) -> int:
        """Number of required qubits."""
        return max(self.input_dim, self.output_dim)


class AmplitudeEmbedding(VQCEncoding, ABC):
    """Abstract base for amplitude embedding."""

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        pad_with: complex,
        *,
        normalize: bool,
    ) -> None:
        """Initialize the amplitude embedding.

        Args:
            input_dim (int): The input dimension of the model.
            output_dim (int): The output dimension of the model.
            pad_with (complex): The input is padded with this constant to size :math:`2^n`.
            normalize (bool): Whether to normalize the features.

        """
        super().__init__(input_dim, output_dim)
        self.pad_with = pad_with
        self.normalize = normalize

    @property
    def num_qubits(self) -> int:
        """Number of required qubits."""
        min_qubits_for_input = math.ceil(math.log2(self.input_dim))
        return max(min_qubits_for_input, self.output_dim)
