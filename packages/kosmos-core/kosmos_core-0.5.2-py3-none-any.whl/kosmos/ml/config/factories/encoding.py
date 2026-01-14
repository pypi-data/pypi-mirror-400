from abc import ABC, abstractmethod
from typing import Literal

from kosmos.circuit_runner.typing import QuantumCircuitFramework
from kosmos.ml.models.vqc.encoding.encoding import AmplitudeEmbedding, AngleEmbedding, VQCEncoding
from kosmos.ml.models.vqc.encoding.pennylane_encoding import (
    PennyLaneAmplitudeEmbedding,
    PennyLaneAngleEmbedding,
)
from kosmos.ml.models.vqc.encoding.qiskit_encoding import (
    QiskitAmplitudeEmbedding,
    QiskitAngleEmbedding,
)


class EncodingConfig(ABC):
    """Abstract base for encoding configurations."""

    def __init__(self) -> None:
        """Initialize the encoding configuration."""
        self.framework = None

    def set_framework(self, framework: QuantumCircuitFramework) -> None:
        """Set the framework for the encoding.

        Args:
            framework (QuantumCircuitFramework): The framework to use for the encoding.

        """
        self.framework = framework

    def _validate_framework(self) -> None:
        """Validate the framework for the encoding."""
        if self.framework is None:
            msg = (
                "Framework must be set for an encoding config via set_framework(...) "
                "before getting an instance."
            )
            raise ValueError(msg)

    @abstractmethod
    def get_instance(self, input_dim: int, output_dim: int) -> VQCEncoding:
        """Get the encoding instance.

        Args:
            input_dim (int): Model input dimension.
            output_dim (int): Model output dimension.

        Returns:
            VQCEncoding: Encoding instance.

        """


class AngleEmbeddingConfig(EncodingConfig):
    """Angle embedding configuration."""

    def __init__(self, rotation: Literal["X", "Y", "Z"] = "X") -> None:
        """Initialize the angle embedding configuration.

        Args:
            rotation (Literal["X", "Y", "Z"]): The rotation to use for the angle embedding.
                Defaults to "X".

        """
        super().__init__()
        self.rotation = rotation

    def get_instance(self, input_dim: int, output_dim: int) -> AngleEmbedding:
        """Get the angle embedding instance.

        Args:
            input_dim (int): Model input dimension.
            output_dim (int): Model output dimension.

        Returns:
            AngleEmbedding: Angle embedding instance.

        """
        self._validate_framework()

        angle_embedding_implementations: dict[str, type[AngleEmbedding]] = {
            "pennylane": PennyLaneAngleEmbedding,
            "qiskit": QiskitAngleEmbedding,
        }

        if self.framework not in angle_embedding_implementations:
            msg = f"Unsupported framework: {self.framework}"
            raise ValueError(msg)

        cls = angle_embedding_implementations[self.framework]

        return cls(input_dim, output_dim, self.rotation)


class AmplitudeEmbeddingConfig(EncodingConfig):
    """Amplitude embedding configuration."""

    def __init__(
        self,
        pad_with: complex = 0.3,
        *,
        normalize: bool = True,
    ) -> None:
        """Initialize the amplitude embedding configuration.

        Args:
            pad_with (complex): The input is padded with this constant to size :math:`2^n`.
            normalize (bool): Whether to normalize the features. Defaults to True.

        """
        super().__init__()
        self.pad_with = pad_with
        self.normalize = normalize

    def get_instance(self, input_dim: int, output_dim: int) -> AmplitudeEmbedding:
        """Get the amplitude embedding instance.

        Args:
            input_dim (int): Model input dimension.
            output_dim (int): Model output dimension.

        Returns:
            AmplitudeEmbedding: Amplitude embedding instance.

        """
        self._validate_framework()

        amplitude_embedding_implementations: dict[str, type[AmplitudeEmbedding]] = {
            "pennylane": PennyLaneAmplitudeEmbedding,
            "qiskit": QiskitAmplitudeEmbedding,
        }

        if self.framework not in amplitude_embedding_implementations:
            msg = f"Unsupported framework: {self.framework}"
            raise ValueError(msg)

        cls = amplitude_embedding_implementations[self.framework]

        return cls(input_dim, output_dim, self.pad_with, normalize=self.normalize)
