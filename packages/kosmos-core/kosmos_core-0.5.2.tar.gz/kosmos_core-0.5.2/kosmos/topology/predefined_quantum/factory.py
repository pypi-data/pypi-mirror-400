from typing import Literal

from kosmos.topology.net import Network
from kosmos.topology.predefined_quantum.builders import (
    LineTopology,
    RingTopology,
    StarTopology,
)


def create_topology(
    topology_type: Literal["line", "ring", "star"], num_nodes: int, num_qubits: int = 127
) -> Network:
    """Create a network from a predefined quantum topology.

    The nodes are connected with quantum and classical links.

    Args:
        topology_type (Literal["line", "ring", "star"]): Kind of topology.
        num_nodes (int): Number of nodes in the topology.
        num_qubits (int): Number of qubits per node. Defaults to 127.

    Returns:
        Network: Constructed network instance.

    """
    match topology_type:
        case "line":
            return LineTopology(num_nodes, num_qubits).build()

        case "ring":
            return RingTopology(num_nodes, num_qubits).build()

        case "star":
            return StarTopology(num_nodes, num_qubits).build()
