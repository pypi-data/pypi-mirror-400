from qiskit import QuantumCircuit
from qiskit.providers import QiskitBackendNotFoundError
from qiskit_ibm_runtime import IBMBackend, QiskitRuntimeService


def qiskit_remote_backend(
    qiskit_runtime_service: QiskitRuntimeService,
    backend_name: str | None = None,
    min_num_qubits: int | None = None,
) -> IBMBackend:
    """Return a remote backend.

    Args:
        qiskit_runtime_service (QiskitRuntimeService): The Qiskit Runtime service instance.
        backend_name (str | None): The name of the backend. Returns the least busy backend if None.
            Defaults to None.
        min_num_qubits (int | None): The minimum number of qubits. Defaults to None.

    Returns:
        IBMBackend: The remote backend.

    """
    if backend_name is None:
        return qiskit_runtime_service.least_busy(min_num_qubits=min_num_qubits, operational=True)

    backends = qiskit_runtime_service.backends(name=backend_name, min_num_qubits=min_num_qubits)
    if not backends:
        msg = "No backend matches the criteria."
        raise QiskitBackendNotFoundError(msg)
    return backends[0]


def available_backends_list(qiskit_runtime_service: QiskitRuntimeService) -> str:
    """Human-readable list of available backends, including pending jobs.

    Args:
        qiskit_runtime_service (QiskitRuntimeService): The Qiskit Runtime service instance.

    Returns:
        str: Human-readable list of available backends, including pending jobs.

    """
    backends = qiskit_runtime_service.backends()

    descr = ""
    for backend in backends:
        descr += f"{backend.name}, pending jobs: {backend.status().pending_jobs}\n"
    if not backends:
        descr = "No backends available.\n"

    return descr


def cancel_job(qiskit_runtime_service: QiskitRuntimeService, job_id: str) -> None:
    """Cancel a runtime job.

    Args:
        qiskit_runtime_service (QiskitRuntimeService): The Qiskit Runtime service instance.
        job_id (str): The job ID.

    """
    job = qiskit_runtime_service.job(job_id)
    job.cancel()


def cancel_all_jobs(qiskit_runtime_service: QiskitRuntimeService) -> None:
    """Cancel all runtime jobs.

    Args:
        qiskit_runtime_service (QiskitRuntimeService): The Qiskit Runtime service instance.

    """
    for job in qiskit_runtime_service.jobs():
        job.cancel()


def minimal_circuit() -> QuantumCircuit:
    """Return a minimal Qiskit circuit suitable to test basic execution.

    The circuit uses one qubit and one classical bit, applies an X gate, and measures the outcome.

    Returns:
        QuantumCircuit: The minimal quantum circuit.

    """
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)
    return qc
