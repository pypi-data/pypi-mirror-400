import unittest

import numpy as np

from causal_profiler.constants import (
    MechanismFamily,
    NeuralNetworkType,
    NoiseDistribution,
    NoiseMode,
    VariableDataType,
    VariableRole,
)
from causal_profiler.scm import SCM
from causal_profiler.variable import Variable


class TestSCM(unittest.TestCase):
    def setUp(self):
        # Set up variables and SCM instance for tests
        self.X = Variable(
            name="X", dimensionality=1, variable_type=VariableDataType.CONTINUOUS
        )
        self.Y = Variable(
            name="Y", dimensionality=1, variable_type=VariableDataType.CONTINUOUS
        )
        self.Z = Variable(
            name="Z", dimensionality=1, variable_type=VariableDataType.CONTINUOUS
        )
        self.variables = [self.X, self.Y, self.Z]
        self.scm = SCM(
            variables=self.variables,
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_mode=NoiseMode.ADDITIVE,
            noise_args=[0, 1],
        )

    def test_variables_initialization(self):
        # Test that variables and noise variables are initialized correctly
        self.assertEqual(len(self.scm.variables), 6)  # 3 variables + 3 noise variables
        self.assertEqual(len(self.scm.noise_variables), 3)
        for var in self.variables:
            noise_var_id = self.scm.parents[var.name][0]
            noise_var = self.scm.variables[noise_var_id]
            self.assertTrue(noise_var.exogenous)
            self.assertEqual(noise_var.name, f"U_{var.name}")
            self.assertIn(var.name, self.scm.children[noise_var_id])
            self.assertEqual(var.variable_role, VariableRole.UNKNOWN)
            self.assertEqual(noise_var.variable_role, VariableRole.UNKNOWN)

    def test_add_exogenous_variable(self):
        # Test that you can add an exogenous variable without adding
        # an automatic exogenous parent to it.
        num_variables_before = len(self.scm.variables)

        self.scm.add_variable(Variable(name="A", exogenous=False))
        self.scm.add_variable(Variable(name="B", exogenous=True))

        num_variables_after = len(self.scm.variables)
        self.assertTrue(num_variables_before + 3 == num_variables_after)

    def test_add_variable_roles(self):
        A = Variable(name="A", exogenous=False, variable_role=VariableRole.CONDITIONED)
        B = Variable(name="B", exogenous=True)
        self.scm.add_variable(A)
        self.scm.add_variable(B)

        self.assertEqual(A.variable_role, VariableRole.CONDITIONED)
        self.assertEqual(B.variable_role, VariableRole.UNKNOWN)

    def test_add_edge(self):
        # Test adding a single edge
        self.scm.add_edge(self.X, self.Y)
        self.assertIn(self.X.name, self.scm.parents[self.Y.name])
        self.assertIn(self.Y.name, self.scm.children[self.X.name])

    def test_add_edges(self):
        # Test adding multiple edges
        edges = [(self.X, self.Y), (self.Y, self.Z)]
        self.scm.add_edges(edges)
        self.assertIn(self.X.name, self.scm.parents[self.Y.name])
        self.assertIn(self.Y.name, self.scm.parents[self.Z.name])

    def test_set_function_linear(self):
        # Test setting a linear mechanism
        self.scm.add_edge(self.X, self.Y)
        self.scm.set_function(self.Y, MechanismFamily.LINEAR)
        self.assertIn(self.Y.name, self.scm.mechanisms)
        self.assertTrue(callable(self.scm.mechanisms[self.Y.name]))

    def test_set_function_nn(self):
        # Test setting a neural network mechanism
        self.scm.add_edge(self.X, self.Y)
        self.scm.set_function(
            self.Y,
            MechanismFamily.NEURAL_NETWORK,
            mechanism_args=[NeuralNetworkType.FEEDFORWARD, 10, 5],
        )
        self.assertIn(self.Y.name, self.scm.mechanisms)
        self.assertTrue(callable(self.scm.mechanisms[self.Y.name]))

    def test_set_function_tabular(self):
        # Test setting a tabuluar mechanism
        # Note that this setting isn't really valid for a tabular mechanism but here
        # we only test that we are able to set the function
        self.scm.add_edge(self.X, self.Y)
        self.scm.set_function(
            self.Y, MechanismFamily.TABULAR, mechanism_args=[([(0, 0)], 1)]
        )
        self.assertIn(self.Y.name, self.scm.mechanisms)
        self.assertTrue(callable(self.scm.mechanisms[self.Y.name]))

    def test_sample_noise_variables(self):
        # Test sampling noise variables
        self.scm.sample_noise_variables()
        for noise_var_id in self.scm.noise_variables:
            noise_var = self.scm.variables[noise_var_id]
            self.assertIsNotNone(noise_var.value)

    def test_compute_variable_linear(self):
        # Test computing a variable with a linear mechanism
        self.scm.add_edge(self.X, self.Y)
        self.scm.set_function(self.X, MechanismFamily.LINEAR)
        self.scm.set_function(self.Y, MechanismFamily.LINEAR)
        self.scm.sample_noise_variables()
        self.scm.compute_variable(self.Y, backwards=True)
        self.assertIsNotNone(self.X.value)
        self.assertIsNotNone(self.Y.value)

    def test_compute_variable_nn(self):
        # Test computing a variable with a neural network mechanism
        self.scm.add_edge(self.X, self.Y)
        self.scm.set_function(self.X, MechanismFamily.LINEAR)
        self.scm.set_function(
            self.Y,
            MechanismFamily.NEURAL_NETWORK,
            mechanism_args=[NeuralNetworkType.FEEDFORWARD, 10, 5],
        )
        self.scm.sample_noise_variables()
        self.scm.compute_variable(self.Y, backwards=True)
        self.assertIsNotNone(self.Y.value)

    def test_noise_modes(self):
        # Test additive and multiplicative noise modes
        self.scm.noise_mode = NoiseMode.ADDITIVE
        self.scm.add_edge(self.X, self.Y)
        self.scm.set_function(self.X, MechanismFamily.LINEAR)
        self.scm.set_function(self.Y, MechanismFamily.LINEAR)
        self.scm.sample_noise_variables()
        self.scm.compute_variable(self.Y, backwards=True)
        value_additive = self.Y.value

        self.scm.reset_values()
        self.scm.noise_mode = NoiseMode.MULTIPLICATIVE
        self.scm.sample_noise_variables()
        self.scm.set_function(self.X, MechanismFamily.LINEAR)
        self.scm.compute_variable(self.Y, backwards=True)
        value_multiplicative = self.Y.value

        self.assertNotEqual(value_additive.tolist(), value_multiplicative.tolist())

    def test_discrete_variable(self):
        # Test handling of discrete variables
        D = Variable(
            name="D",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        self.scm.add_variable(D)
        # Manually set the noise regions of the U_D
        [U_D_name] = self.scm.parents[D.name]
        self.scm.variables[U_D_name].noise_regions = [0.0]
        self.scm.set_function(
            D,
            MechanismFamily.TABULAR,
            mechanism_args=[
                (
                    [(0,)],
                    0,
                )
            ],
        )
        self.scm.sample_noise_variables()
        noise_var_id = self.scm.parents[D.name][0]
        noise_var = self.scm.variables[noise_var_id]
        # Check that all its values come from a N(0, 1) normal
        # Flatten the (N, 1) array to a 1D array
        values = noise_var.value.flatten()
        # Calculate z-scores: (value - mean) / std deviation
        z_scores = (values - 0) / 1  # Mean = 0, Std Dev = 1 for N(0, 1)
        # Set a higher threshold to reduce false negatives
        threshold = 4  # Allow values within ±4 standard deviations
        # Check proportion of values within the threshold
        within_threshold = np.abs(z_scores) <= threshold
        proportion_within = np.mean(within_threshold)
        # Define an acceptable proportion of values outside the threshold (e.g., <1%)
        acceptable_false_positive_rate = 0.01
        # Assert that the proportion of values outside the threshold is acceptable
        self.assertTrue(
            proportion_within >= 1 - acceptable_false_positive_rate,
            f"Too many values fall outside ±{threshold} standard deviations. Proportion within: {proportion_within:.3f}",
        )

    def test_tabular_function(self):
        # Test setting a tabular mechanism
        A = Variable(
            name="A",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        B = Variable(
            name="B",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        C = Variable(
            name="C",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        self.scm = SCM(
            variables=[A, B, C],
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[0, 1],
        )
        # Manually set the noise regions of the noise of each variable
        [U_A_name] = self.scm.parents[A.name]
        self.scm.variables[U_A_name].noise_regions = [1.0]
        [U_B_name] = self.scm.parents[B.name]
        self.scm.variables[U_B_name].noise_regions = [1.0]
        [U_C_name] = self.scm.parents[C.name]
        self.scm.variables[U_C_name].noise_regions = [1.0]

        self.scm.add_edges([(A, C), (B, C)])
        # Incomplete mechanisms but you know that U_C will be 0 because of the noise region
        mechanism_args = [
            ([(0, 0, 0)], 1),
            ([(0, 1, 0), (1, 0, 0)], 2),
            ([(1, 1, 0)], 3),
        ]
        self.scm.set_function(C, MechanismFamily.TABULAR, mechanism_args=mechanism_args)
        self.scm.sample_noise_variables()
        # Intervention
        self.scm.do_hard_intervention(A, 1)
        self.scm.do_hard_intervention(B, 0)
        self.scm.compute_variable(C, backwards=True)
        self.assertEqual(C.value, 2)

    def test_reset_values(self):
        # Test resetting variable values
        self.scm.add_edge(self.X, self.Y)
        self.scm.set_function(self.X, MechanismFamily.LINEAR)
        self.scm.set_function(self.Y, MechanismFamily.LINEAR)
        self.scm.sample_noise_variables()
        self.scm.compute_variable(self.Y, backwards=True)
        self.scm.reset_values()
        self.assertIsNone(self.X.value)
        self.assertIsNone(self.Y.value)
        for noise_var_id in self.scm.noise_variables:
            noise_var = self.scm.variables[noise_var_id]
            self.assertIsNone(noise_var.value)

    def test_invalid_mechanism_family(self):
        # Test setting an invalid function family
        with self.assertRaises(ValueError):
            self.scm.set_function(self.X, "invalid_family")

    def test_invalid_noise_mode(self):
        # Test setting an invalid noise mode
        self.scm.noise_mode = "invalid_mode"
        self.scm.add_edge(self.X, self.Y)
        self.scm.set_function(self.Y, MechanismFamily.LINEAR)
        self.scm.sample_noise_variables()
        with self.assertRaises(ValueError):
            self.scm.compute_variable(self.Y, backwards=True)

    def test_extract_adjacency_list(self):
        # Case 1: Simple linear graph
        X = Variable("X")
        Y = Variable("Y")
        Z = Variable("Z")
        scm = SCM(variables=[X, Y, Z])
        scm.add_edge(X, Y)
        scm.add_edge(Y, Z)

        expected_edge_list = [(0, 1), (1, 2)]
        expected_adjacency = {node: [] for node in [0, 1, 2]}
        for u, v in sorted(expected_edge_list):
            expected_adjacency[u].append(v)
        adj_list, idx_to_variable_id = scm.extract_adjacency_list()
        assert adj_list == expected_adjacency, f"Test case 1 failed: {adj_list}"
        assert idx_to_variable_id == ["X", "Y", "Z"]

        # Case 2: Graph with exogenous variables and a clique
        U_XW = Variable("U_XW", exogenous=True, visible=False)
        U_YW = Variable("U_YW", exogenous=True, visible=False)
        X = Variable("X")
        Y = Variable("Y")
        W = Variable("W")
        Z = Variable("Z")
        scm = SCM(variables=[U_XW, U_YW, X, Y, W, Z])
        scm.add_edge(U_XW, X)
        scm.add_edge(U_XW, W)
        scm.add_edge(X, Y)
        scm.add_edge(Y, Z)
        scm.add_edge(U_YW, Y)
        scm.add_edge(U_YW, W)

        expected_edge_list = [
            (0, 1),  # Clique edge X -> W
            (1, 2),  # Clique edge W -> Y
            (2, 1),  # Clique edge Y -> W
            (2, 3),  # Y -> Z
            (0, 2),  # X -> Y
            (1, 0),  # Clique edge W -> X
        ]
        expected_adjacency = {node: [] for node in [0, 1, 2, 3]}
        for u, v in sorted(expected_edge_list):
            expected_adjacency[u].append(v)
        adj_list, idx_to_variable_id = scm.extract_adjacency_list()
        assert adj_list == expected_adjacency, f"Test case 2 failed: {adj_list}"
        assert idx_to_variable_id == ["X", "W", "Y", "Z"]

        # Case 3: Fully connected graph with one exogenous variable
        U = Variable("U", exogenous=True, visible=False)
        A = Variable("A")
        B = Variable("B")
        C = Variable("C")
        scm = SCM(variables=[U, A, B, C])
        scm.add_edge(U, A)
        scm.add_edge(U, B)
        scm.add_edge(U, C)
        scm.add_edge(A, B)
        scm.add_edge(B, C)

        expected_edge_list = [
            (0, 1),
            (1, 0),
            (1, 2),
            (2, 1),
            (0, 2),
            (2, 0),
        ]
        expected_adjacency = {node: [] for node in [0, 1, 2]}
        for u, v in sorted(expected_edge_list):
            expected_adjacency[u].append(v)
        adj_list, idx_to_variable_id = scm.extract_adjacency_list()
        assert adj_list == expected_adjacency, f"Test case 3 failed: {adj_list}"
        assert idx_to_variable_id == ["A", "B", "C"]

    def test_extract_adjacency_list_with_hidden_variables(self):
        # Case 1: Single hidden variable
        X = Variable("X")
        H = Variable("H", visible=False)
        Y = Variable("Y")
        scm = SCM(variables=[X, H, Y])
        scm.add_edge(X, H)
        scm.add_edge(H, Y)

        expected_adjacency = {0: [1], 1: []}  # X -> Y (through H)  # Y has no children
        adj_list, idx_to_variable_id = scm.extract_adjacency_list()
        assert adj_list == expected_adjacency, f"Test case 1 failed: {adj_list}"
        assert idx_to_variable_id == ["X", "Y"]

        # Case 2: Chain of hidden variables
        X = Variable("X")
        H1 = Variable("H1", visible=False)
        H2 = Variable("H2", visible=False)
        Y = Variable("Y")
        scm = SCM(variables=[X, H1, H2, Y])
        scm.add_edge(X, H1)
        scm.add_edge(H1, H2)
        scm.add_edge(H2, Y)

        expected_adjacency = {
            0: [1],  # X -> Y (through H1 and H2)
            1: [],  # Y has no children
        }
        adj_list, idx_to_variable_id = scm.extract_adjacency_list()
        assert adj_list == expected_adjacency, f"Test case 2 failed: {adj_list}"
        assert idx_to_variable_id == ["X", "Y"]

        # Case 3: Hidden variable with multiple children
        H = Variable("H", visible=False)
        A = Variable("A")
        B = Variable("B")
        C = Variable("C")
        scm = SCM(variables=[H, A, B, C])
        scm.add_edge(H, A)
        scm.add_edge(H, B)
        scm.add_edge(H, C)

        expected_adjacency = {
            0: [1, 2],  # A, B, C are mutually connected due to H
            1: [0, 2],
            2: [0, 1],
        }
        adj_list, idx_to_variable_id = scm.extract_adjacency_list()
        assert adj_list == expected_adjacency, f"Test case 3 failed: {adj_list}"
        assert idx_to_variable_id == ["A", "B", "C"]

        # Case 4: Combination of visible and hidden variables
        U = Variable("U", exogenous=True, visible=False)
        H1 = Variable("H1", visible=False)
        H2 = Variable("H2", visible=False)
        X = Variable("X")
        Y = Variable("Y")
        Z = Variable("Z")
        scm = SCM(variables=[U, H1, H2, X, Y, Z])
        scm.add_edge(U, H1)
        scm.add_edge(H1, X)
        scm.add_edge(H1, H2)
        scm.add_edge(H2, Y)
        scm.add_edge(H2, Z)

        expected_adjacency = {
            # 0: [1, 2, 3],  # U -> X, U -> Y, U -> Z (through H1 and H2)
            0: [1, 2],  # X -> Y, X -> Z (through H2)
            1: [0, 2],  # Y <-> Z (confounded through H2)
            2: [0, 1],
        }
        adj_list, idx_to_variable_id = scm.extract_adjacency_list()
        assert adj_list == expected_adjacency, f"Test case 4 failed: {adj_list}"
        assert idx_to_variable_id == ["X", "Y", "Z"]

        # Case 5: Complex graph with exogenous and hidden variables
        U = Variable("U", exogenous=True, visible=False)
        V = Variable("V", exogenous=True, visible=False)
        H = Variable("H", visible=False)
        X = Variable("X")
        Y = Variable("Y")
        Z = Variable("Z")
        scm = SCM(variables=[U, V, H, X, Y, Z])
        scm.add_edge(U, H)
        scm.add_edge(V, H)
        scm.add_edge(H, X)
        scm.add_edge(H, Y)
        scm.add_edge(X, Z)

        expected_adjacency = {
            0: [1, 2],  # X -> Y, X -> Z (through H)
            1: [0],  # X <-> Y (confounded through H)
            2: [],  # Z has no outgoing edges
        }
        adj_list, idx_to_variable_id = scm.extract_adjacency_list()
        assert adj_list == expected_adjacency, f"Test case 5 failed: {adj_list}"
        assert idx_to_variable_id == ["X", "Y", "Z"]

        # Case 6: Chain of hidden endogenous variables
        # test_extract_adjacency_list_with_chain_of_hidden_variables
        X = Variable("X")
        H1 = Variable("H1", visible=False)
        H2 = Variable("H2", visible=False)
        Y = Variable("Y")
        scm = SCM(variables=[X, H1, H2, Y])
        scm.add_edge(X, H1)
        scm.add_edge(H1, H2)
        scm.add_edge(H2, Y)

        expected_adjacency = {
            0: [1],  # X -> Y (transitive through H1 and H2)
            1: [],  # Y has no children
        }
        adj_list, idx_to_variable_id = scm.extract_adjacency_list()
        assert adj_list == expected_adjacency, f"Test case 6 failed: {adj_list}"
        assert idx_to_variable_id == ["X", "Y"]

    def test_extract_adjacency_matrix(self):
        # Case 1: Simple linear graph
        X = Variable("X")
        Y = Variable("Y")
        Z = Variable("Z")
        scm = SCM(variables=[X, Y, Z])
        scm.add_edge(X, Y)
        scm.add_edge(Y, Z)

        expected_matrix = [
            [0, 1, 0],  # X -> Y
            [0, 0, 1],  # Y -> Z
            [0, 0, 0],  # Z has no outgoing edges
        ]
        adj_matrix, idx_to_variable_id = scm.extract_adjacency_matrix()
        assert adj_matrix == expected_matrix, f"Test case 1 failed: {adj_matrix}"
        assert idx_to_variable_id == ["X", "Y", "Z"]

        # Case 2: Graph with exogenous variables and a clique
        U_XW = Variable("U_XW", exogenous=True, visible=False)
        U_YW = Variable("U_YW", exogenous=True, visible=False)
        X = Variable("X")
        Y = Variable("Y")
        W = Variable("W")
        Z = Variable("Z")
        scm = SCM(variables=[U_XW, U_YW, X, Y, W, Z])
        scm.add_edge(U_XW, X)
        scm.add_edge(U_XW, W)
        scm.add_edge(X, Y)
        scm.add_edge(Y, Z)
        scm.add_edge(U_YW, Y)
        scm.add_edge(U_YW, W)

        expected_matrix = [
            [0, 1, 1, 0],  # X: W, Y
            [1, 0, 1, 0],  # W: X, Y
            [0, 1, 0, 1],  # Y: W, Z
            [0, 0, 0, 0],
        ]
        adj_matrix, idx_to_variable_id = scm.extract_adjacency_matrix()
        assert adj_matrix == expected_matrix, f"Test case 2 failed: {adj_matrix}"
        assert idx_to_variable_id == ["X", "W", "Y", "Z"]

        # Case 3: Fully connected graph with one exogenous variable
        U = Variable("U", exogenous=True, visible=False)
        A = Variable("A")
        B = Variable("B")
        C = Variable("C")
        scm = SCM(variables=[U, A, B, C])
        scm.add_edge(U, A)
        scm.add_edge(U, B)
        scm.add_edge(U, C)
        scm.add_edge(A, B)
        scm.add_edge(B, C)

        expected_matrix = [
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0],
        ]
        adj_matrix, idx_to_variable_id = scm.extract_adjacency_matrix()
        assert adj_matrix == expected_matrix, f"Test case 3 failed: {adj_matrix}"
        assert idx_to_variable_id == ["A", "B", "C"]

        print("All test cases passed!")

    def test_extract_adjacency_matrix_with_hidden_variables(self):
        # Case 1: Single hidden variable
        X = Variable("X")
        H = Variable("H", visible=False)
        Y = Variable("Y")
        scm = SCM(variables=[X, H, Y])
        scm.add_edge(X, H)
        scm.add_edge(H, Y)

        expected_matrix = [
            [0, 1],  # X -> Y (via H)
            [0, 0],  # Y has no outgoing edges
        ]
        adj_matrix, idx_to_variable_id = scm.extract_adjacency_matrix()
        assert adj_matrix == expected_matrix, f"Test case 1 failed: {adj_matrix}"
        assert idx_to_variable_id == ["X", "Y"]

        # Case 2: Chain of hidden variables
        X = Variable("X")
        H1 = Variable("H1", visible=False)
        H2 = Variable("H2", visible=False)
        Y = Variable("Y")
        scm = SCM(variables=[X, H1, H2, Y])
        scm.add_edge(X, H1)
        scm.add_edge(H1, H2)
        scm.add_edge(H2, Y)

        expected_matrix = [
            [0, 1],  # X -> Y (transitive through H1 and H2)
            [0, 0],  # Y has no outgoing edges
        ]
        adj_matrix, idx_to_variable_id = scm.extract_adjacency_matrix()
        assert adj_matrix == expected_matrix, f"Test case 2 failed: {adj_matrix}"
        assert idx_to_variable_id == ["X", "Y"]

        # Case 3: Hidden variable with multiple children
        H = Variable("H", visible=False)
        A = Variable("A")
        B = Variable("B")
        C = Variable("C")
        scm = SCM(variables=[H, A, B, C])
        scm.add_edge(H, A)
        scm.add_edge(H, B)
        scm.add_edge(H, C)

        expected_matrix = [
            [0, 1, 1],  # A -> B, A -> C
            [1, 0, 1],  # B -> A, B -> C
            [1, 1, 0],  # C -> A, C -> B
        ]
        adj_matrix, idx_to_variable_id = scm.extract_adjacency_matrix()
        assert adj_matrix == expected_matrix, f"Test case 3 failed: {adj_matrix}"
        assert idx_to_variable_id == ["A", "B", "C"]

        # Case 4: Combination of visible and hidden variables
        U = Variable("U", exogenous=True, visible=False)
        H1 = Variable("H1", visible=False)
        H2 = Variable("H2", visible=False)
        X = Variable("X")
        Y = Variable("Y")
        Z = Variable("Z")
        scm = SCM(variables=[U, H1, H2, X, Y, Z])
        scm.add_edge(U, H1)
        scm.add_edge(H1, X)
        scm.add_edge(H1, H2)
        scm.add_edge(H2, Y)
        scm.add_edge(H2, Z)

        expected_matrix = [
            [0, 1, 1],  # X <-> Y, Z
            [1, 0, 1],  # Y <-> X, Z
            [1, 1, 0],  # Z <-> X, Y
        ]
        adj_matrix, idx_to_variable_id = scm.extract_adjacency_matrix()
        print(adj_matrix)
        print(expected_matrix)
        assert adj_matrix == expected_matrix, f"Test case 4 failed: {adj_matrix}"
        assert idx_to_variable_id == ["X", "Y", "Z"]

        # Case 5: Complex graph with exogenous and hidden variables
        U = Variable("U", exogenous=True, visible=False)
        V = Variable("V", exogenous=True, visible=False)
        H = Variable("H", visible=False)
        X = Variable("X")
        Y = Variable("Y")
        Z = Variable("Z")
        scm = SCM(variables=[U, V, H, X, Y, Z])
        scm.add_edge(U, H)
        scm.add_edge(V, H)
        scm.add_edge(H, X)
        scm.add_edge(H, Y)
        scm.add_edge(X, Z)

        expected_matrix = [
            [0, 1, 1],  # X -> Y, X -> Z
            [1, 0, 0],  # Y -> X
            [0, 0, 0],  # Z has no outgoing edges
        ]
        adj_matrix, idx_to_variable_id = scm.extract_adjacency_matrix()
        assert adj_matrix == expected_matrix, f"Test case 5 failed: {adj_matrix}"
        assert idx_to_variable_id == ["X", "Y", "Z"]

        print("All hidden variable tests passed!")

    def test_do_hard_intervention(self):
        # (n_samples, dimensionality)
        self.scm.n_samples = 2

        # Test with scalar value
        self.scm.do_hard_intervention(self.X, 5)
        expected_value = np.full((self.scm.n_samples, self.X.dimensionality), 5)
        self.assertTrue(np.array_equal(self.X.value, expected_value))

        # Test with 1D array
        self.scm.do_hard_intervention(self.X, [5])
        self.assertTrue(np.array_equal(self.X.value, expected_value))

        # Test with pre-broadcasted 2D array
        pre_broadcasted_value = np.array([[5], [5]])
        self.scm.n_samples = 2
        self.scm.do_hard_intervention(self.X, pre_broadcasted_value)
        self.assertTrue(np.array_equal(self.X.value, pre_broadcasted_value))

        # Test with invalid shape for pre-broadcasted array
        invalid_value = np.array([[5, 5]])
        with self.assertRaises(ValueError):
            self.scm.do_hard_intervention(self.X, invalid_value)

        # Test with mismatched batch size
        mismatched_value = np.array([[5], [5], [5]])
        with self.assertRaises(ValueError):
            self.scm.do_hard_intervention(self.X, mismatched_value)


if __name__ == "__main__":
    unittest.main()
