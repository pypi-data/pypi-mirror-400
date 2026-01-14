from importlib.resources import as_file, files

from qiskit import QuantumCircuit


class MQTBenchCircuit:
    """Loader for benchmarking circuits from MQT Bench."""

    def __init__(self, circuit_type: str, num_qubits: int) -> None:
        """Initialize the benchmarking circuit loader.

        Args:
            circuit_type (str): Type of circuit to load (e.g., "qft", "dj").
            num_qubits (int): Number of qubits in the desired circuit.

        """
        if not circuit_type or not circuit_type.strip():
            msg = "circuit_type must be a non-empty string"
            raise ValueError(msg)

        if num_qubits <= 0:
            msg = f"num_qubits must be positive, got {num_qubits}"
            raise ValueError(msg)

        self.circuit_type = circuit_type.lower()
        self.num_qubits = num_qubits
        self._circuit: QuantumCircuit | None = None

    def _construct_filename(self) -> str:
        """Construct the QASM filename for this circuit.

        Returns:
            str: Filename in MQT Bench format.

        """
        return f"{self.circuit_type}_indep_qiskit_{self.num_qubits}.qasm"

    def _load_circuit(self) -> QuantumCircuit:
        """Load the circuit from QASM file.

        Returns:
            QuantumCircuit: Loaded quantum circuit.

        """
        mqt_bench_files = files("kosmos.partitioning.mqt_bench") / "data"
        circuit_file = mqt_bench_files / self._construct_filename()

        with as_file(circuit_file) as filepath:
            if not filepath.exists():
                msg = f"Circuit file not found: {self._construct_filename()}\n"
                raise FileNotFoundError(msg)

            return QuantumCircuit.from_qasm_file(str(filepath))

    def circuit(self) -> QuantumCircuit:
        """Get the quantum circuit (lazy loading).

        Returns:
            QuantumCircuit: The loaded circuit.

        """
        if self._circuit is None:
            self._circuit = self._load_circuit()
        return self._circuit

    @property
    def num_gates(self) -> int:
        """Total number of gates in the circuit without barriers."""
        return sum(
            count for name, count in self.circuit().count_ops().items() if name != "barrier"
        )

    @property
    def depth(self) -> int:
        """Circuit depth."""
        return self.circuit().depth()
