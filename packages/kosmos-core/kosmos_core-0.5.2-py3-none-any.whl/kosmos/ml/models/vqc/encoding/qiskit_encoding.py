from collections.abc import Sequence

import numpy as np
from qiskit import QuantumCircuit
from torch import Tensor

from kosmos.circuit_runner.typing import QuantumCircuitFramework
from kosmos.ml.models.vqc.encoding.encoding import AmplitudeEmbedding, AngleEmbedding


class QiskitAngleEmbedding(AngleEmbedding):
    """Angle embedding for the VQC using Qiskit."""

    @property
    def framework(self) -> QuantumCircuitFramework:
        """The framework used for the quantum circuit."""
        return "qiskit"

    def apply_operation(
        self, features: Tensor, wires: Sequence[int], qc: QuantumCircuit | None = None
    ) -> None:
        """Apply the Qiskit angle embedding operation for encoding.

        Args:
            features (Tensor): Input features.
            wires (Sequence[int]): Target wires.
            qc (QuantumCircuit | None): The quantum circuit to use for the encoding
                (only for 'qiskit' framework).

        """
        super().apply_operation(features, wires, qc)

        if len(features) > len(wires):
            m = f"Got {len(features)} features for {len(wires)} wires."
            raise ValueError(m)

        for i, f in enumerate(features):
            w = wires[i]

            angle = f.item() if isinstance(f, Tensor) else f

            wire = int(w)

            if self.rotation == "X":
                qc.rx(angle, wire)
            elif self.rotation == "Y":
                qc.ry(angle, wire)
            elif self.rotation == "Z":
                qc.rz(angle, wire)
            else:
                msg = f"Unknown rotation axis: {self.rotation}"
                raise ValueError(msg) from None


class QiskitAmplitudeEmbedding(AmplitudeEmbedding):
    """Amplitude embedding for the VQC using Qiskit."""

    @property
    def framework(self) -> QuantumCircuitFramework:
        """The framework used for the quantum circuit."""
        return "qiskit"

    def apply_operation(
        self, features: Tensor, wires: Sequence[int], qc: QuantumCircuit | None = None
    ) -> None:
        """Apply the Qiskit amplitude embedding operation for encoding.

        Args:
            features (Tensor): Input features.
            wires (Sequence[int]): Target wires.
            qc (QuantumCircuit | None): The quantum circuit to use for the encoding
                (only for 'qiskit' framework).

        """
        super().apply_operation(features, wires, qc)

        def preprocessing(x: Tensor) -> np.ndarray:
            x = np.pad(x, (0, 2**self.num_qubits - len(x))).astype(np.float64)
            norm = np.linalg.norm(x)
            if norm == 0:
                msg = "Cannot normalize zero vector."
                raise ValueError(msg)
            return x / norm

        qc.initialize(preprocessing(features), wires)
