import numpy as np
from qiskit_ibm_runtime import RuntimeJobV2 as RuntimeJob


def calculate_expectation_values(counts: dict[str, int]) -> np.ndarray:
    """Calculate Z-basis expectation values for each qubit from counts.

    Args:
        counts (dict[str, int]): Mapping from bitstring to number of shots.

    Returns:
        np.ndarray: Array of expectation values (one per qubit).

    """
    total_shots = sum(counts.values())
    bitstrings = list(counts.keys())

    bit_matrix = np.array(
        [
            [int(bit) for bit in bitstring[::-1]]  # Reverse bitstring as Qiskit uses little-endian
            for bitstring in bitstrings
        ]
    )
    shot_counts = np.array([counts[bitstring] for bitstring in bitstrings]).reshape(-1, 1)

    z_basis_values = 1 - 2 * bit_matrix
    expectations = np.sum(z_basis_values * shot_counts, axis=0) / total_shots
    return expectations.astype(np.float32)


def job_expectation_values(job: RuntimeJob) -> list[np.ndarray]:
    """Calculate expectation values from job results.

    Args:
        job (RuntimeJob): The job to get results for.

    Returns:
        list[np.ndarray]: A list of arrays, where each array contains the expectation
            values for one circuit in the job.

    """
    result = job.result()

    expectation_values = []
    for result_item in result:
        counts = result_item.data["c"].get_counts()
        expectation_values.append(calculate_expectation_values(counts))

    return expectation_values
