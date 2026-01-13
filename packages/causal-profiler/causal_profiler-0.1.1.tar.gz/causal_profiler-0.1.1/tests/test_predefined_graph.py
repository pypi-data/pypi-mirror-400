"""
Tests for predefined graph functionality.
Test loading graphs from YAML files and using them in the causal profiler.
"""

import os
import tempfile
import pytest
import numpy as np

from causal_profiler.causal_profiler import CausalProfiler
from causal_profiler.constants import (
    MechanismFamily,
    NoiseDistribution,
    NoiseMode,
    QueryType,
    VariableDataType,
)
from causal_profiler.sampler import Sampler
from causal_profiler.space_of_interest import SpaceOfInterest
from causal_profiler.utils import load_graph_from_yaml, is_dag


class TestDAGValidation:
    """Test DAG validation utility functions."""

    def test_valid_dag(self):
        """Test that a valid DAG is correctly identified."""
        graph = {"A": ["B"], "B": ["C"], "C": []}
        assert is_dag(graph) is True

    def test_self_loop(self):
        """Test that self-loops are detected as cycles."""
        graph = {"A": ["A"]}
        assert is_dag(graph) is False

    def test_two_node_cycle(self):
        """Test that a simple two-node cycle is detected."""
        graph = {"A": ["B"], "B": ["A"]}
        assert is_dag(graph) is False

    def test_three_node_cycle(self):
        """Test that a three-node cycle is detected."""
        graph = {"A": ["B"], "B": ["C"], "C": ["A"]}
        assert is_dag(graph) is False

    def test_complex_dag(self):
        """Test a complex but valid DAG."""
        graph = {"A": ["C", "D"], "B": ["C", "D"], "C": ["E"], "D": ["E"], "E": []}
        assert is_dag(graph) is True

    def test_disconnected_dag(self):
        """Test a DAG with disconnected components."""
        graph = {"A": ["B"], "B": [], "C": ["D"], "D": []}
        assert is_dag(graph) is True

    def test_empty_graph(self):
        """Test an empty graph."""
        graph = {}
        assert is_dag(graph) is True


class TestGraphLoading:
    """Test loading graphs from YAML files."""

    def test_simple_graph_loading(self):
        """Test loading a simple graph from YAML."""
        yaml_content = """
            edges:
            - [X, Y]
            - [Y, Z]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            graph, hidden_nodes = load_graph_from_yaml(temp_path)
            assert "X" in graph
            assert "Y" in graph
            assert "Z" in graph
            assert "Y" in graph["X"]
            assert "Z" in graph["Y"]
            assert len(hidden_nodes) == 0
        finally:
            os.unlink(temp_path)

    def test_graph_with_hidden_nodes(self):
        """Test loading a graph with hidden nodes."""
        yaml_content = """
            edges:
            - [X, Y]
            - [U, X]
            - [U, Y]

            node_attrs:
                U:
                    hidden: true
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            graph, hidden_nodes = load_graph_from_yaml(temp_path)
            assert "X" in graph
            assert "Y" in graph
            assert "U" in graph
            assert "U" in hidden_nodes
            assert "X" not in hidden_nodes
            assert "Y" not in hidden_nodes
        finally:
            os.unlink(temp_path)

    def test_graph_with_multiple_hidden_nodes(self):
        """Test loading a graph with multiple hidden nodes."""
        yaml_content = """
            edges:
            - [A, C]
            - [B, C]

            node_attrs:
                A:
                    hidden: true
                B:
                    hidden: true
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            graph, hidden_nodes = load_graph_from_yaml(temp_path)
            assert "A" in hidden_nodes
            assert "B" in hidden_nodes
            assert "C" not in hidden_nodes
        finally:
            os.unlink(temp_path)

    def test_cycle_detection_in_yaml(self):
        """Test that cycles in YAML graphs are detected."""
        yaml_content = """
            edges:
            - [X, Y]
            - [Y, Z]
            - [Z, X]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="contains cycles"):
                load_graph_from_yaml(temp_path)
        finally:
            os.unlink(temp_path)

    def test_missing_edges_field(self):
        """Test that missing edges field raises an error."""
        yaml_content = """
            node_attrs:
                U:
                    hidden: true
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="must contain 'edges'"):
                load_graph_from_yaml(temp_path)
        finally:
            os.unlink(temp_path)

    def test_invalid_edge_format(self):
        """Test that invalid edge format raises an error."""
        yaml_content = """
            edges:
            - [X]
            - [Y, Z]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="must be a list of 2 nodes"):
                load_graph_from_yaml(temp_path)
        finally:
            os.unlink(temp_path)

    def test_nonexistent_file(self):
        """Test that loading from a non-existent file raises an error."""
        with pytest.raises(FileNotFoundError):
            load_graph_from_yaml("/nonexistent/path/to/file.yaml")


class TestSpaceOfInterestWithPredefinedGraph:
    """Test SpaceOfInterest with predefined graph functionality."""

    def test_space_with_predefined_graph_file(self):
        """Test creating a SpaceOfInterest with a predefined graph file."""
        yaml_content = """
            edges:
            - [X, Y]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=1,
                query_type=QueryType.ATE,
            )
            assert space.predefined_graph_file == temp_path
        finally:
            os.unlink(temp_path)

    def test_space_without_predefined_graph(self):
        """Test creating a SpaceOfInterest without a predefined graph."""
        space = SpaceOfInterest(
            predefined_graph_file=None,
            variable_type=VariableDataType.DISCRETE,
            number_of_categories=2,
            mechanism_family=MechanismFamily.TABULAR,
        )
        assert space.predefined_graph_file is None

    def test_space_serialization_with_predefined_graph(self):
        """Test that predefined graph file is included in serialization."""
        yaml_content = """
            edges:
            - [X, Y]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
            )
            space_dict = space.to_dict()
            assert "predefined_graph_file" in space_dict
            assert space_dict["predefined_graph_file"] == temp_path
        finally:
            os.unlink(temp_path)

    def test_space_equality_with_predefined_graph(self):
        """Test that two spaces with the same predefined graph are equal."""
        yaml_content = """
            edges:
            - [X, Y]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space1 = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
            )
            space2 = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
            )
            assert space1 == space2
        finally:
            os.unlink(temp_path)


class TestSamplerWithPredefinedGraph:
    """Test Sampler with predefined graphs."""

    def test_sampler_generates_scm_from_predefined_graph(self):
        """Test that sampler correctly generates SCM from a predefined graph."""
        yaml_content = """
            edges:
            - [X, Y]
            - [Y, Z]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=1,
                query_type=QueryType.ATE,
                number_of_data_points=100,
            )
            sampler = Sampler(space_of_interest=space)
            scm = sampler.generate_scm()

            # Check that the SCM has the correct variables
            assert "X" in scm.variables
            assert "Y" in scm.variables
            assert "Z" in scm.variables

            # Check that edges are correctly set up
            assert "Y" in scm.children["X"]
            assert "Z" in scm.children["Y"]
        finally:
            os.unlink(temp_path)

    def test_sampler_respects_hidden_nodes(self):
        """Test that sampler correctly marks hidden nodes as invisible."""
        yaml_content = """
            edges:
            - [X, Y]
            - [U, X]
            - [U, Y]

            node_attrs:
                U:
                    hidden: true
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=1,
                query_type=QueryType.ATE,
                number_of_data_points=100,
            )
            sampler = Sampler(space_of_interest=space)
            scm = sampler.generate_scm()

            # Check that U is hidden
            assert not scm.variables["U"].visible
            # Check that X and Y are visible
            assert scm.variables["X"].visible
            assert scm.variables["Y"].visible

        finally:
            os.unlink(temp_path)

    def test_generate_samples_and_queries_with_predefined_graph(self):
        """Test full pipeline with predefined graph."""
        yaml_content = """
            edges:
            - [X, Y]
            - [Y, Z]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=1,
                query_type=QueryType.ATE,
                number_of_data_points=100,
            )
            sampler = Sampler(space_of_interest=space)
            data, (queries, estimates), graph = sampler.generate_samples_and_queries()

            # Check data
            assert "X" in data
            assert "Y" in data
            assert "Z" in data
            assert data["X"].shape[0] == 100

            # Check queries
            assert len(queries) >= 1
            assert len(estimates) >= 1

            # Check graph structure
            adj, names = graph
            assert "X" in names
            assert "Y" in names
            assert "Z" in names
            x = names.index("X")
            y = names.index("Y")
            z = names.index("Z")
            assert y in adj.get(x, [])
            assert y not in adj.get(z, [])
            assert z in adj.get(y, [])
            assert z not in adj.get(x, [])
            assert x not in adj.get(y, [])
            assert x not in adj.get(z, [])
        finally:
            os.unlink(temp_path)

    def test_generate_samples_and_queries_with_predefined_graph_and_hidden_var(self):
        """Test full pipeline with predefined graph and a hidden variable."""
        yaml_content = """
            edges:
            - [U, X]
            - [U, Y]

            node_attrs:
                U:
                    hidden: true
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=1,
                query_type=QueryType.ATE,
                number_of_data_points=100,
            )
            sampler = Sampler(space_of_interest=space)
            data, (queries, estimates), graph = sampler.generate_samples_and_queries()

            # Check data
            assert "X" in data
            assert "Y" in data
            assert data["X"].shape[0] == 100

            # Check queries
            assert len(queries) >= 1
            assert len(estimates) >= 1

            # Check graph structure
            adj, names = graph
            assert "X" in names
            assert "Y" in names
            x = names.index("X")
            y = names.index("Y")
            # This happens because of the hidden variable and the projection algorithm
            assert y in adj.get(x, [])
            assert x in adj.get(y, [])
        finally:
            os.unlink(temp_path)

    def test_generate_samples_excludes_hidden_nodes(self):
        """Test that hidden nodes are excluded from the returned data."""
        yaml_content = """
            edges:
            - [X, Y]
            - [U, X]

            node_attrs:
                U:
                    hidden: true
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=1,
                query_type=QueryType.ATE,
                number_of_data_points=100,
            )
            sampler = Sampler(space_of_interest=space)
            data, (queries, estimates), graph = sampler.generate_samples_and_queries()

            # Check that U is not in the returned data
            assert "U" not in data
            # Check that X and Y are in the data
            assert "X" in data
            assert "Y" in data
        finally:
            os.unlink(temp_path)


class TestCausalProfilerWithPredefinedGraph:
    """Test CausalProfiler with predefined graphs."""

    def test_causal_profiler_with_predefined_graph(self):
        """Test CausalProfiler with a predefined graph."""
        yaml_content = """
            edges:
            - [X, Y]
            - [Y, Z]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=2,
                query_type=QueryType.ATE,
                number_of_data_points=100,
            )
            profiler = CausalProfiler(space_of_interest=space)
            data, (queries, estimates), graph = profiler.generate_samples_and_queries()

            # Check that we get valid outputs
            assert len(data) > 0
            assert len(queries) >= 1
            assert len(estimates) >= 1

            # Test error evaluation
            # Create dummy predictions (same as actual for zero error)
            error, num_failed = profiler.evaluate_error(estimates, estimates)
            assert error < 1e-6  # Should be very close to zero
            assert num_failed == 0
        finally:
            os.unlink(temp_path)

    def test_multiple_runs_with_same_predefined_graph(self):
        """Test that multiple runs with the same graph produce different data."""
        yaml_content = """
            edges:
            - [X, Y]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=1,
                query_type=QueryType.ATE,
                number_of_data_points=100,
            )
            profiler = CausalProfiler(space_of_interest=space)

            # Generate two datasets
            data1, _, _ = profiler.generate_samples_and_queries()
            data2, _, _ = profiler.generate_samples_and_queries()

            # Data should be different (due to different random samples)
            # but graph structure should be the same
            assert not np.array_equal(data1["X"], data2["X"])
        finally:
            os.unlink(temp_path)


class TestComplexGraphStructures:
    """Test various complex graph structures."""

    def test_diamond_structure(self):
        """Test a diamond-shaped graph structure."""
        yaml_content = """
            edges:
            - [A, B]
            - [A, C]
            - [B, D]
            - [C, D]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=1,
                query_type=QueryType.ATE,
                number_of_data_points=100,
            )
            sampler = Sampler(space_of_interest=space)
            scm = sampler.generate_scm()

            # Verify structure
            assert "B" in scm.children["A"]
            assert "C" in scm.children["A"]
            assert "D" in scm.children["B"]
            assert "D" in scm.children["C"]
        finally:
            os.unlink(temp_path)

    def test_large_graph(self):
        """Test a larger graph structure."""
        yaml_content = """
            edges:
            - [X1, X2]
            - [X1, X3]
            - [X2, X4]
            - [X3, X4]
            - [X4, X5]
            - [X5, X6]
            """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            space = SpaceOfInterest(
                predefined_graph_file=temp_path,
                variable_type=VariableDataType.DISCRETE,
                number_of_categories=2,
                mechanism_family=MechanismFamily.TABULAR,
                number_of_queries=1,
                query_type=QueryType.ATE,
                number_of_data_points=100,
            )
            sampler = Sampler(space_of_interest=space)
            data, (queries, estimates), graph = sampler.generate_samples_and_queries()

            # Check all nodes are present
            assert len(data) == 6
            for i in range(1, 7):
                assert f"X{i}" in data
        finally:
            os.unlink(temp_path)
