from typing import Any

from qiskit import QuantumCircuit

from kosmos.partitioning.graph import Graph


def to_gate_list(circuit: QuantumCircuit) -> list[dict[str, Any]]:
    """Extract gate list from a QuantumCircuit, skipping barriers.

    Args:
        circuit: QuantumCircuit to convert.

    Returns:
        list[dict[str, object]]: List of gates.

    """
    gates = []
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name == "barrier":
            continue
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        gates.append({"name": operation.name, "qubits": qubits})
    return gates


def to_graph(circuit: QuantumCircuit) -> Graph:
    """Convert to undirected graph for partitioning algorithms.

    Args:
        circuit: QuantumCircuit to convert.

    Returns:
        Graph: Graph representation of the circuit.

    """
    gates = to_gate_list(circuit)
    adjacency = {i: set() for i in range(len(gates))}

    for i, gate_i in enumerate(gates):
        for j, gate_j in enumerate(gates):
            if i == j:
                continue
            if set(gate_i["qubits"]) & set(gate_j["qubits"]):
                adjacency[i].add(j)
                adjacency[j].add(i)

    adjacency_list = [list(neigh) for neigh in adjacency.values()]
    return Graph(adjacency_list)
