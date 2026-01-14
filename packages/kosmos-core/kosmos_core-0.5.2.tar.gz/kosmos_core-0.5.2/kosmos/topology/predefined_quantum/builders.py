from abc import ABC, abstractmethod

from kosmos.topology.link import ClassicalLink, LinkId, QuantumLink
from kosmos.topology.net import Network
from kosmos.topology.node import NodeId, NodeRole, QuantumNode

DEFAULT_COHERENCE_TIME: float = 1.0

QUANTUM_LINK_DEFAULT_DISTANCE: float = 10.0
QUANTUM_LINK_DEFAULT_ATTENUATION: float = 0.0
QUANTUM_LINK_DEFAULT_SIGNAL_SPEED: float = 2e-4
QUANTUM_LINK_DEFAULT_REPETITION_RATE: float = 1e6

CLASSICAL_LINK_DEFAULT_DISTANCE: float = 10.0
CLASSICAL_LINK_DEFAULT_ATTENUATION: float = 2e-4
CLASSICAL_LINK_DEFAULT_SIGNAL_SPEED: float = 2e-4
CLASSICAL_LINK_DEFAULT_BANDWIDTH: float = 10e9


def _default_node(i: int, role: NodeRole, num_qubits: int) -> QuantumNode:
    """Create a default quantum node for predefined quantum topologies.

    Args:
        i (int): Index to convert to a NodeId.
        role (NodeRole): Assigned role of the node.
        num_qubits (int): Number of qubits for the node.

    Returns:
        QuantumNode: Quantum node instance.

    """
    return QuantumNode(
        id=NodeId(str(i)),
        roles=[role],
        num_qubits=num_qubits,
        coherence_time=DEFAULT_COHERENCE_TIME,
    )


def _default_quantum_link(src: QuantumNode, dst: QuantumNode) -> QuantumLink:
    """Create a default quantum link for predefined quantum topologies.

    Args:
        src (QuantumNode): Source node.
        dst (QuantumNode): Destination node.

    Returns:
        QuantumLink: Quantum link instance.

    """
    return QuantumLink(
        id=LinkId(f"Q_{src.id.value}-{dst.id.value}"),
        src=src,
        dst=dst,
        distance=QUANTUM_LINK_DEFAULT_DISTANCE,
        attenuation=QUANTUM_LINK_DEFAULT_ATTENUATION,
        signal_speed=QUANTUM_LINK_DEFAULT_SIGNAL_SPEED,
        repetition_rate=QUANTUM_LINK_DEFAULT_REPETITION_RATE,
    )


def _default_classical_link(src: QuantumNode, dst: QuantumNode) -> ClassicalLink:
    """Create a default classical link for predefined quantum topologies.

    Args:
        src (QuantumNode): Source node.
        dst (QuantumNode): Destination node.

    Returns:
        ClassicalLink: Classical link instance.

    """
    return ClassicalLink(
        id=LinkId(f"C_{src.id.value}-{dst.id.value}"),
        src=src,
        dst=dst,
        distance=CLASSICAL_LINK_DEFAULT_DISTANCE,
        attenuation=CLASSICAL_LINK_DEFAULT_ATTENUATION,
        signal_speed=CLASSICAL_LINK_DEFAULT_SIGNAL_SPEED,
        bandwidth=CLASSICAL_LINK_DEFAULT_BANDWIDTH,
    )


class PredefinedQuantumTopology(ABC):
    """Abstract base class for predefined quantum topologies."""

    @abstractmethod
    def build(self) -> Network:
        """Construct the topology and return a Network instance.

        Returns:
            Network: Constructed network instance.

        """


class LineTopology(PredefinedQuantumTopology):
    """Line quantum topology."""

    def __init__(self, num_nodes: int, num_qubits: int) -> None:
        """Initialize the line quantum topology.

        Args:
            num_nodes (int): Number of nodes (must be >= 2).
            num_qubits (int): Number of qubits for the node.

        """
        min_num_nodes = 2
        if num_nodes < min_num_nodes:
            msg = "Line topology requires at least 2 nodes."
            raise ValueError(msg)

        self.num_nodes = num_nodes
        self.num_qubits = num_qubits

    def build(self) -> Network:
        """Build the line quantum topology.

        Returns:
            Network: Network with nodes connected in a linear chain.

        """
        network = Network()

        # endpoints = END_USER, inner nodes = REPEATER
        nodes: list[QuantumNode] = []
        for i in range(self.num_nodes):
            role = NodeRole.END_USER if i == 0 or i == self.num_nodes - 1 else NodeRole.REPEATER
            node = _default_node(i, role, self.num_qubits)
            network.add_node(node)
            nodes.append(node)

        # Create links between consecutive nodes
        for i in range(self.num_nodes - 1):
            q_link = _default_quantum_link(nodes[i], nodes[i + 1])
            c_link = _default_classical_link(nodes[i], nodes[i + 1])
            network.add_link(q_link)
            network.add_link(c_link)

        return network


class RingTopology(PredefinedQuantumTopology):
    """Ring quantum topology."""

    def __init__(self, num_nodes: int, num_qubits: int) -> None:
        """Initialize the ring quantum topology.

        Args:
            num_nodes (int): Number of nodes (must be >= 3).
            num_qubits (int): Number of qubits for the node.

        """
        min_num_nodes = 3
        if num_nodes < min_num_nodes:
            msg = "Ring topology requires at least 3 nodes."
            raise ValueError(msg)
        self.num_nodes = num_nodes
        self.num_qubits = num_qubits

    def build(self) -> Network:
        """Build the ring quantum topology.

        Returns:
            Network: Network forming a closed cycle.

        """
        network = Network()

        # All nodes in a ring are ROUTERs.
        nodes: list = []
        for i in range(self.num_nodes):
            node = _default_node(i, NodeRole.ROUTER, self.num_qubits)
            network.add_node(node)
            nodes.append(node)

        for i in range(self.num_nodes):
            src = nodes[i]
            dst = nodes[(i + 1) % self.num_nodes]
            q_link = _default_quantum_link(src, dst)
            c_link = _default_classical_link(src, dst)
            network.add_link(q_link)
            network.add_link(c_link)

        return network


class StarTopology(PredefinedQuantumTopology):
    """Star quantum topology."""

    def __init__(self, num_nodes: int, num_qubits: int) -> None:
        """Initialize the star quantum topology.

        Args:
            num_nodes (int): Number of nodes (must be >= 2).
            num_qubits (int): Number of qubits for the node.

        """
        min_num_nodes = 2
        if num_nodes < min_num_nodes:
            msg = "Star topology requires at least 2 nodes."
            raise ValueError(msg)
        self.num_nodes = num_nodes
        self.num_qubits = num_qubits

    def build(self) -> Network:
        """Build the star quantum topology.

        Returns:
            Network: Network with one central node and all other nodes connected to the center.

        """
        network = Network()

        # The center node is a ROUTER, all other nodes are END_USERS
        nodes: list = []
        node_center = _default_node(0, NodeRole.ROUTER, self.num_qubits)
        network.add_node(node_center)
        nodes.append(node_center)
        for i in range(1, self.num_nodes):
            node = _default_node(i, NodeRole.END_USER, self.num_qubits)
            network.add_node(node)
            nodes.append(node)
        for i in range(1, self.num_nodes):
            q_link = _default_quantum_link(nodes[0], nodes[i])
            c_link = _default_classical_link(nodes[0], nodes[i])
            network.add_link(q_link)
            network.add_link(c_link)
        return network
