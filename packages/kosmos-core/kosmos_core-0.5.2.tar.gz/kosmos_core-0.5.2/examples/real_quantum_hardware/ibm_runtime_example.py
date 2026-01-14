from qiskit_ibm_runtime import QiskitRuntimeService

from kosmos.circuit_runner.ibm_runtime_utils import available_backends_list, minimal_circuit
from kosmos.circuit_runner.qiskit_runner import IBMRuntimeRunner


def ibm_runtime_example() -> None:
    """Run example of using IBM Runtime to execute a minimal circuit."""
    circuit = minimal_circuit()

    # Initialize the Qiskit Runtime service used to access the IBM Quantum platform
    # See https://quantum.cloud.ibm.com/docs/de/api/qiskit-ibm-runtime/qiskit-runtime-service
    qiskit_runtime_service = QiskitRuntimeService()

    # Print available backends
    print(available_backends_list(qiskit_runtime_service))  # noqa: T201

    # Initialize the IBM Runtime runner that can be used to execute circuits
    runner = IBMRuntimeRunner(
        qiskit_runtime_service=qiskit_runtime_service,
        backend_name=None,  # Use the least busy backend
        min_num_qubits=circuit.num_qubits,
        num_shots=256,
    )

    # Run the circuit using real hardware and compute expectation values
    expectation_values = runner.expectation_values([circuit])

    print(f"Expectation value: {expectation_values[0][0]:.3f}")  # noqa: T201


if __name__ == "__main__":
    ibm_runtime_example()
