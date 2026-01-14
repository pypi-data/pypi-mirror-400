from collections.abc import Sequence

import pennylane
from qiskit import QuantumCircuit
from torch import Tensor

from kosmos.circuit_runner.typing import QuantumCircuitFramework
from kosmos.ml.models.vqc.encoding.encoding import AmplitudeEmbedding, AngleEmbedding


class PennyLaneAngleEmbedding(AngleEmbedding):
    """Angle embedding for the VQC using PennyLane."""

    @property
    def framework(self) -> QuantumCircuitFramework:
        """The framework used for the quantum circuit."""
        return "pennylane"

    def apply_operation(
        self, features: Tensor, wires: Sequence[int], qc: QuantumCircuit | None = None
    ) -> None:
        """Apply the PennyLane angle embedding operation for encoding.

        Args:
            features (Tensor): Input features.
            wires (Sequence[int]): Target wires.
            qc (QuantumCircuit | None): The quantum circuit to use for the encoding
                (only for 'qiskit' framework).

        """
        super().apply_operation(features, wires, qc)
        pennylane.AngleEmbedding(features, wires, rotation=self.rotation)


class PennyLaneAmplitudeEmbedding(AmplitudeEmbedding):
    """Amplitude embedding for the VQC using PennyLane."""

    @property
    def framework(self) -> QuantumCircuitFramework:
        """The framework used for the quantum circuit."""
        return "pennylane"

    def apply_operation(
        self, features: Tensor, wires: Sequence[int], qc: QuantumCircuit | None = None
    ) -> None:
        """Apply the PennyLane amplitude embedding operation for encoding.

        Args:
            features (Tensor): Input features.
            wires (Sequence[int]): Target wires.
            qc (QuantumCircuit | None): The quantum circuit to use for the encoding
                (only for 'qiskit' framework).

        """
        super().apply_operation(features, wires, qc)
        pennylane.AmplitudeEmbedding(
            features, wires, pad_with=self.pad_with, normalize=self.normalize
        )
