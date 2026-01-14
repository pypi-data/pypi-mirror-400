import math
from abc import ABC, abstractmethod

from qiskit import QuantumCircuit

from kosmos.partitioning.circuit_converter import to_graph
from kosmos.partitioning.graph import Graph
from kosmos.topology.net import Network
from kosmos.topology.node import NodeType


class PartitioningAlgorithm(ABC):
    """Base class for circuit partitioning algorithms."""

    def __init__(self, network: Network | None, num_partitions: int | None) -> None:
        """Initialize the partitioning algorithm.

        Args:
            network (Network | None): The network topology. Required if num_partitions is None.
            num_partitions (int | None): Number of partitions to create. If None, the number of
                quantum nodes in the network is used.

        """
        self.network = network
        self.num_partitions = num_partitions

        if self.num_partitions is None:
            if self.network is None:
                msg = "network must be provided if num_partitions is None."
                raise ValueError(msg)
            num_quantum_nodes = len(
                [node for node in self.network.nodes() if node.type == NodeType.QUANTUM]
            )
            if num_quantum_nodes < 1:
                msg = "The network must contain at least one quantum node."
                raise ValueError(msg)
            self.num_partitions = num_quantum_nodes

        if self.num_partitions < 1 or not math.isfinite(self.num_partitions):
            msg = "num_partitions must be >= 1 and finite."
            raise ValueError(msg)

    @staticmethod
    def _to_graph(circuit: Graph | QuantumCircuit) -> Graph:
        """Return a graph representation of the given circuit.

        If ``circuit`` is already a graph, it is returned unchanged.
        Otherwise, the circuit is converted into a graph.

        Args:
            circuit (Graph | QuantumCircuit): Circuit to convert.

        Returns:
            Graph: Graph representation of the circuit.

        """
        if isinstance(circuit, Graph):
            return circuit
        return to_graph(circuit)

    @abstractmethod
    def partition(self, circuit: Graph | QuantumCircuit) -> dict[int, int]:
        """Compute a partitioning for the given circuit.

        Args:
            circuit (Graph | QuantumCircuit): Circuit to partition.

        Returns:
            dict[int, int]: A mapping from each node index to the partition identifier it is
                assigned to.

        """

    def __call__(self, circuit: Graph | QuantumCircuit) -> dict[int, int]:
        """Execute the partitioning algorithm.

        Args:
            circuit (Graph | QuantumCircuit): Circuit to partition.

        Returns:
            dict[int, int]: A mapping from each node index to the partition identifier it is
                assigned to.

        """
        return self.partition(circuit)
