from kosmos.partitioning.algorithms.capacity_partitioner import CapacityBasedPartitioner
from kosmos.partitioning.mqt_bench.bench_circuit import MQTBenchCircuit
from kosmos.utils.rng import RNG

GATE_VISUALIZATION_LENGTH = 5


def partitioning_result_description(
    algorithm_name: str, assignments: dict[int, int], num_gates: int
) -> list[str]:
    """Format partitioning results as human-readable text lines.

    Args:
        algorithm_name: Name of the partitioning algorithm.
        assignments: Gate-to-partition assignments.
        num_gates: Total number of gates in the circuit.

    Returns:
        list[str]: Formatted output lines.

    """
    output = [f"\n{'=' * 60}", f"Algorithm: {algorithm_name}", f"{'=' * 60}"]

    # Group gates by partition
    partitions: dict[int, list[int]] = {}
    for gate_idx, partition_id in assignments.items():
        if partition_id not in partitions:
            partitions[partition_id] = []
        partitions[partition_id].append(gate_idx)

    # Calculate statistics
    num_partitions = len(partitions)
    partition_sizes = [len(gates) for gates in partitions.values()]
    avg_size = sum(partition_sizes) / num_partitions if num_partitions > 0 else 0
    max_size = max(partition_sizes) if partition_sizes else 0
    min_size = min(partition_sizes) if partition_sizes else 0

    output.append("\nStatistics:")
    output.append(f"  Total gates: {num_gates}")
    output.append(f"  Number of partitions: {num_partitions}")
    output.append(f"  Partition sizes: min={min_size}, max={max_size}, avg={avg_size:.1f}")

    # Calculate balance metric
    if avg_size > 0:
        balance = max(abs(size - avg_size) for size in partition_sizes) / avg_size
        output.append(f"  Balance (max deviation): {balance:.2%}")

    output.append("\nPartition Details:")
    for partition_id in sorted(partitions.keys()):
        gates = sorted(partitions[partition_id])
        gate_str = (
            f"[{gates[0]}...{gates[-1]}]" if len(gates) > GATE_VISUALIZATION_LENGTH else str(gates)
        )
        output.append(f"  Partition {partition_id}: {len(gates)} gates {gate_str}")

    return output


def capacity_based_grover_example() -> None:
    """Run example for naive capacity-based circuit partitioning on a Grover circuit."""
    RNG.initialize(seed=1)

    output = ["\n=== Circuit Characteristics ==="]

    # Load Grover circuit from MQT Bench
    benchmark = MQTBenchCircuit(circuit_type="grover-noancilla", num_qubits=8)
    circuit = benchmark.circuit()

    output.append(f"Qubits: {benchmark.num_qubits}")
    output.append(f"Gates: {benchmark.num_gates}")
    output.append(f"Depth: {benchmark.depth}")

    partitioner = CapacityBasedPartitioner(network=None, num_partitions=3)
    assignments = partitioner.partition(circuit)

    output.extend(
        partitioning_result_description("Capacity-Based", assignments, benchmark.num_gates)
    )

    print("\n".join(output))  # noqa: T201


if __name__ == "__main__":
    capacity_based_grover_example()
