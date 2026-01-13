import unittest

import numpy as np

from causal_profiler.constants import NoiseMode
from causal_profiler.mechanism import *
from causal_profiler.variable import Variable


class TestAddNoiseToMechanism(unittest.TestCase):
    def setUp(self):
        pass

    def test_additive_noise(self):
        expression = np.ones((10, 3))  # Deterministic expression
        noise1 = Variable(name="Noise1", value=np.ones((10, 1)) * 2, dimensionality=1)
        noise2 = Variable(name="Noise2", value=np.ones((10, 3)) * 3, dimensionality=3)

        result = add_noise_to_mechanism(
            expression, [noise1, noise2], NoiseMode.ADDITIVE
        )

        expected = np.ones((10, 3)) + 2 + 3  # Each entry should be 6
        np.testing.assert_array_equal(result, expected)

    def test_multiplicative_noise(self):
        expression = np.ones((5, 2))  # Deterministic expression
        noise1 = Variable(name="Noise1", value=np.ones((5, 1)) * 2, dimensionality=1)
        noise2 = Variable(name="Noise2", value=np.ones((5, 2)) * 3, dimensionality=2)

        result = add_noise_to_mechanism(
            expression, [noise1, noise2], NoiseMode.MULTIPLICATIVE
        )

        expected = np.ones((5, 2)) * 2 * 3  # Each entry should be 6
        np.testing.assert_array_equal(result, expected)

    def test_unchanged_when_no_noise(self):
        expression = np.ones((10, 3))
        result = add_noise_to_mechanism(expression, [], NoiseMode.ADDITIVE)

        assert np.array_equal(result, expression)

    def test_unchanged_when_functional_noise(self):
        expression = np.ones((10, 3))  # Deterministic expression
        noise1 = Variable(name="Noise1", value=np.ones((10, 1)) * 2, dimensionality=1)
        noise2 = Variable(name="Noise2", value=np.ones((10, 3)) * 3, dimensionality=3)

        result = add_noise_to_mechanism(
            expression, [noise1, noise2], NoiseMode.FUNCTIONAL
        )

        assert np.array_equal(result, expression)


class TestLinearFunction(unittest.TestCase):
    def test_linear_function(self):
        X = Variable(name="X", value=np.random.randn(10, 3), dimensionality=3)
        Y = Variable(name="Y", value=np.random.randn(10, 2), dimensionality=2)
        linear_function = create_linear_function(
            variable_dimensionality=4,
            parents=[X, Y],
            noise_mode=NoiseMode.ADDITIVE,
        )
        output = linear_function()
        self.assertEqual(output.shape, (10, 4))  # Check batch_size and output_dim


class TestNNFunction(unittest.TestCase):
    def test_nn_function(self):
        X = Variable(name="X", value=np.random.randn(10, 3), dimensionality=3)
        Y = Variable(name="Y", value=np.random.randn(10, 2), dimensionality=2)
        nn_function = create_nn_function(
            variable_dimensionality=4,
            parents=[X, Y],
            noise_mode=NoiseMode.ADDITIVE,
            mechanism_args=[NeuralNetworkType.FEEDFORWARD, 10, 10],  # Hidden layers
        )
        output = nn_function()
        self.assertEqual(output.shape, (10, 4))  # Check batch_size and output_dim


class TestTabularFunction(unittest.TestCase):
    def test_tabular_mechanism(self):
        # Define dummy parent variables with values
        X = Variable(
            name="X", value=np.array([[0, 0], [1, 1], [0, 1]]), dimensionality=2
        )
        Y = Variable(name="Y", value=np.array([[0], [1], [0]]), dimensionality=1)

        # Define tabular mechanism arguments
        mechanism_args = [
            ([(0, 0, 0)], 1),
            ([(1, 1, 1)], 2),
            ([(0, 1, 0)], 3),
        ]

        # Create the mechanism
        tabular_mechanism = create_tabular_function(
            parents=[X, Y], mechanism_args=mechanism_args
        )

        # Compute the output
        output = tabular_mechanism()

        # Expected output
        expected_output = np.array([[1], [2], [3]])

        # Assert equality
        np.testing.assert_array_equal(output, expected_output)
        self.assertEqual(output.dtype, np.int64)


class TestExogenousDiscretization(unittest.TestCase):
    def test_exogenous_discretization_for_discrete_child(self):
        """
        Verify that if the child variable is DISCRETE, then exogenous variables
        (which are stored as continuous) get discretized according to their noise_regions.
        """
        # Create a discrete child variable
        Z = Variable(
            name="Z",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        # Create a single exogenous (noise) variable with continuous values
        exog_values = np.array(
            [
                [0.5],
                [1.5],
                [2.1],
                [3.9],
            ]
        )  # shape (4,1)
        exog_var = Variable(
            name="NoiseExog",
            dimensionality=1,
            exogenous=True,
            value=exog_values,
        )
        exog_var.noise_regions = np.array([1.0, 2.0, 3.0])  # 3 thresholds

        # Build a mechanism for Z (child) that depends on exog_var
        # (In the refactored code, create_linear_function takes `variable` or child_var as the first param)
        linear_fn = create_linear_function(
            variable_dimensionality=1,  # Z has dimensionality=1
            parents=[exog_var],  # Only the exogenous parent
            noise_mode=NoiseMode.ADDITIVE,
            discrete_output=True,
        )

        # Call the mechanism, which should discretize exog_var on-the-fly
        output = linear_fn()

        # After discretization with thresholds [1,2,3], the exog values become [0,1,2,3]
        expected_discrete = np.array(
            [
                [0],
                [1],
                [2],
                [3],
            ]
        )

        # Check that exog_var.value was indeed discretized in-place
        np.testing.assert_array_equal(exog_var.value, expected_discrete)

        # Also check the shape of the mechanism output; it should match (batch_size, variable_dim=1)
        self.assertEqual(output.shape, (4, 1))

    def test_exogenous_not_discretized_for_continuous_child(self):
        """
        Verify that if the child variable is CONTINUOUS, then exogenous variables
        remain continuous and are NOT discretized, even if noise_regions exist.
        """
        # Create a continuous child variable
        Z = Variable(
            name="Z",
            dimensionality=1,
            variable_type=VariableDataType.CONTINUOUS,
            num_discrete_values=2,
        )

        # Exogenous variable with continuous values and thresholds
        exog_values = np.array(
            [
                [0.5],
                [1.5],
                [2.1],
                [3.9],
            ]
        )  # shape (4,1)
        exog_var = Variable(
            name="NoiseExog",
            dimensionality=1,
            exogenous=True,
            value=exog_values.copy(),  # store a copy for later comparison
        )
        exog_var.noise_regions = [1.0, 2.0, 3.0]

        # Build a mechanism for a continuous child that depends on exog_var
        linear_fn = create_linear_function(
            variable_dimensionality=1,
            parents=[exog_var],
            noise_mode=NoiseMode.ADDITIVE,
            discrete_output=False,
        )

        # Call the mechanism
        output = linear_fn()

        # Since child is continuous, exog_var should remain continuous
        np.testing.assert_array_equal(exog_var.value, exog_values)

        # The output shape should match (batch_size, variable_dim=1)
        self.assertEqual(output.shape, (4, 1))

    def test_exogenous_discretized_in_create_mechanism(self):
        """
        Verify that if the child variable is DISCRETE, then exogenous variables
        (which are stored as continuous) get discretized according to their noise_regions.
        """
        # Create a discrete child variable
        Z = Variable(
            name="Z",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        # Create a single exogenous (noise) variable with continuous values
        exog_values = np.array(
            [
                [0.5],
                [1.5],
                [2.1],
                [3.9],
            ]
        )  # shape (4,1)
        exog_var = Variable(
            name="NoiseExog",
            dimensionality=1,
            exogenous=True,
            value=exog_values,
        )
        exog_var.noise_regions = [1.0, 2.0, 3.0]

        # Build a mechanism for Z (child) that depends on exog_var
        # (In the refactored code, create_linear_function takes `variable` or child_var as the first param)
        linear_fn = create_mechanism(
            variable=Z,
            parents=[exog_var],
            mechanism_family=MechanismFamily.LINEAR,
            noise_mode=NoiseMode.FUNCTIONAL,
        )

        # Call the mechanism, which should discretize exog_var on-the-fly
        output = linear_fn()

        # After discretization with thresholds [1,2,3], the exog values become [0,1,2,3]
        expected_discrete = np.array(
            [
                [0],
                [1],
                [2],
                [3],
            ]
        )

        # Check that exog_var.value was indeed discretized in-place
        np.testing.assert_array_equal(exog_var.value, expected_discrete)

        # Also check the shape of the mechanism output; it should match (batch_size, variable_dim=1)
        self.assertEqual(output.shape, (4, 1))


if __name__ == "__main__":
    unittest.main()
