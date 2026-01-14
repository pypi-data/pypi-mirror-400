from typing import override

from qiskit import QuantumCircuit

from kosmos.partitioning.algorithms.partitioning_algorithm import PartitioningAlgorithm
from kosmos.partitioning.graph import Graph


class CapacityBasedPartitioner(PartitioningAlgorithm):
    """Naive capacity-based partitioner.

    Distributes nodes evenly across partitions, ignoring connectivity.
    """

    @override
    def partition(self, circuit: Graph | QuantumCircuit) -> dict[int, int]:
        """Compute a partitioning for the given circuit.

        Args:
            circuit (Graph | QuantumCircuit): Circuit to partition.

        Returns:
            dict[int, int]: A mapping from each node index to the partition identifier it is
                assigned to.

        """
        graph = self._to_graph(circuit)

        adjacency = graph.to_adjacency_list()
        num_nodes = len(adjacency)
        partition_size = max(1, num_nodes // self.num_partitions)

        assignment: dict[int, int] = {}
        current_partition = 0
        count = 0

        for node in range(num_nodes):
            assignment[node] = current_partition
            count += 1
            if count >= partition_size and current_partition < self.num_partitions - 1:
                current_partition += 1
                count = 0

        return assignment
