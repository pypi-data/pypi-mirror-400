from typing import override

import numpy as np
from qiskit import QuantumCircuit
from scipy.linalg import eigh
from scipy.sparse import csgraph

from kosmos.partitioning.algorithms.partitioning_algorithm import PartitioningAlgorithm
from kosmos.partitioning.graph import Graph


class SpectralPartitioner(PartitioningAlgorithm):
    """Graph partitioning using the Laplacian spectral method."""

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
        adjacency_list = graph.to_adjacency_list()
        n = len(adjacency_list)
        if n <= 1:
            return dict.fromkeys(range(n), 0)
        adjacency = np.zeros((n, n))
        for i, neighbors in enumerate(adjacency_list):
            for j in neighbors:
                adjacency[i, j] = 1

        laplacian = csgraph.laplacian(adjacency, normed=False)

        _, vecs = eigh(laplacian)
        fiedler_vector = vecs[:, 1]

        median_val = np.median(fiedler_vector)
        return {i: int(fiedler_vector[i] > median_val) for i in range(n)}
