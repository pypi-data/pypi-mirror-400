class Graph:
    """Undirected graph representation."""

    def __init__(self, adjacency: list[list[int]]) -> None:
        """Create an undirected graph.

        Args:
           adjacency: Adjacency list representation.

        """
        self.adjacency = adjacency

    @property
    def num_nodes(self) -> int:
        """Number of nodes."""
        return len(self.adjacency)

    @property
    def num_edges(self) -> int:
        """Number of edges."""
        return sum(len(neigh) for neigh in self.adjacency) // 2

    def to_adjacency_list(self) -> list[list[int]]:
        """Create adjacency list for algorithms like PyMetis.

        Returns:
            list[list[int]]: Adjacency list representation.

        """
        return self.adjacency
