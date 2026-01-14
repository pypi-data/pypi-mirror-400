from collections.abc import Callable
from typing import Any, Literal

import pennylane as qml

from kosmos.circuit_runner.circuit_runner import CircuitRunner
from kosmos.circuit_runner.typing import QuantumCircuitFramework


class PennyLaneRunner(CircuitRunner):
    """Runner for PennyLane."""

    def __init__(
        self, device_name: Literal["default.qubit", "lightning.qubit"] = "lightning.qubit"
    ) -> None:
        """Initialize the PennyLane runner.

        Args:
            device_name (Literal["default.qubit", "lightning.qubit"]): Name of the PennyLane
                device. Defaults to "lightning.qubit".

        """
        self.device_name = device_name
        self.device: qml.devices.Device | None = None
        self.qnode: qml.QNode | None = None

    @property
    def framework(self) -> QuantumCircuitFramework:
        """The framework used by the circuit runner."""
        return "pennylane"

    def configure_qnode(self, num_wires: int, circuit: Callable[..., Any]) -> None:
        """Configure the QNode for a given circuit.

        Args:
            num_wires (int): Number of wires (qubits) in the circuit.
            circuit (Callable[..., Any]): Callable defining the quantum circuit.

        """
        self.device = qml.device(self.device_name, wires=num_wires)
        self.qnode = qml.QNode(circuit, self.device, interface="torch")

    def execute(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """Execute the configured QNode with the given arguments.

        Args:
            *args (Any): Positional arguments passed to the underlying QNode.
            **kwargs (Any): Keyword arguments passed to the underlying QNode.

        Returns:
            Any: The result returned by the QNode.

        """
        if self.qnode is None:
            msg = "QNode has not been configured. Call configure_qnode(...) first."
            raise RuntimeError(msg)

        return self.qnode(*args, **kwargs)
