import numpy as np
import yaml
from typing import Dict, List, Set, Tuple


def ensure_list(*args):
    """
    Ensures all input arguments are lists.
    If an argument is not a list, it is wrapped in a list.

    Args:
        *args: Arbitrary number of arguments to check.

    Returns:
        A tuple where each argument is a list.
    """
    return tuple(arg if isinstance(arg, list) else [arg] for arg in args)


def broadcast_value_to_batch(value, batch_size):
    """
    Covert scalars and 1D arrays to (batch_size, <previous dimension>)
    """
    # Convert scalars to 1D arrays
    if np.isscalar(value):
        value = np.array([value])  # Convert scalar to 1D array

    # Ensure value is a 1D numpy array
    value = np.asarray(value)
    if value.ndim != 1:
        raise ValueError("Value must be a scalar or a 1D array.")

    # Broadcast to the desired shape
    return np.tile(value, (batch_size, 1))


def load_graph_from_yaml(filepath: str) -> Tuple[Dict[str, List[str]], Set[str]]:
    """
    Load a graph structure from a YAML file.

    Args:
        filepath: Path to the YAML file containing the graph definition.

    Returns:
        A tuple of (graph_dict, hidden_nodes) where:
        - graph_dict: Dictionary mapping parent nodes to lists of children
        - hidden_nodes: Set of node names that are hidden

    Raises:
        ValueError: If the graph contains cycles (is not a DAG)
        FileNotFoundError: If the file doesn't exist

    Example YAML format:
        edges:
          - [X, Y]
          - [U, X]
          - [U, Y]

        node_attrs:
          U:
            hidden: true

    Note:
        The complete graph (including all hidden variables) must form a valid DAG.
        For example, if you have X <- U -> Y and X -> Y, explicitly model the
        hidden confounder U as a node with edges U -> X, U -> Y, and X -> Y.
    """
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    if "edges" not in data:
        raise ValueError("YAML file must contain 'edges' field")

    edges = data["edges"]
    node_attrs = data.get("node_attrs", {})

    # Build adjacency list (parent -> children)
    graph_dict = {}
    all_nodes = set()

    for edge in edges:
        if len(edge) != 2:
            raise ValueError(f"Each edge must be a list of 2 nodes, got: {edge}")
        parent, child = edge
        all_nodes.add(parent)
        all_nodes.add(child)

        if parent not in graph_dict:
            graph_dict[parent] = []
        graph_dict[parent].append(child)

    # Ensure all nodes are in the graph dict (even if they have no children)
    for node in all_nodes:
        if node not in graph_dict:
            graph_dict[node] = []

    # Extract hidden nodes
    hidden_nodes = set()
    for node, attrs in node_attrs.items():
        if attrs.get("hidden", False):
            hidden_nodes.add(node)

    # Validate that it's a DAG
    if not is_dag(graph_dict):
        raise ValueError(
            "The provided graph contains cycles and is not a valid DAG. "
            "Make sure to explicitly include all nodes (including hidden confounders)."
        )

    return graph_dict, hidden_nodes


def is_dag(graph: Dict[str, List[str]]) -> bool:
    """
    Check if a directed graph is a DAG (Directed Acyclic Graph).

    Args:
        graph: Dictionary mapping nodes to lists of their children

    Returns:
        True if the graph is a DAG, False if it contains cycles
    """
    # Use DFS with color marking to detect cycles
    # WHITE (0): unvisited, GRAY (1): in current DFS path, BLACK (2): completed
    color = {node: 0 for node in graph.keys()}

    def has_cycle_dfs(node: str) -> bool:
        """DFS helper to detect cycles."""
        color[node] = 1  # Mark as GRAY (visiting)

        for neighbor in graph.get(node, []):
            if neighbor not in color:
                color[neighbor] = 0

            if color[neighbor] == 1:  # Back edge found (cycle)
                return True
            if color[neighbor] == 0 and has_cycle_dfs(neighbor):
                return True

        color[node] = 2  # Mark as BLACK (completed)
        return False

    # Check all nodes (for disconnected components)
    for node in graph.keys():
        if color[node] == 0:
            if has_cycle_dfs(node):
                return False

    return True
