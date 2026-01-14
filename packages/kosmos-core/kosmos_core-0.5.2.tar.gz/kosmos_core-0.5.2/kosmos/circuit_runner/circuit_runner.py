from abc import ABC, abstractmethod

from kosmos.circuit_runner.typing import QuantumCircuitFramework


class CircuitRunner(ABC):
    """Abstract base class for circuit runners."""

    @property
    @abstractmethod
    def framework(self) -> QuantumCircuitFramework:
        """The framework used by the circuit runner."""
