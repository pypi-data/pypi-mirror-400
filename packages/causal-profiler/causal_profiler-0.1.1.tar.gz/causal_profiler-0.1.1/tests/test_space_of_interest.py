import os
import unittest
import warnings

from causal_profiler.constants import (
    FunctionSampling,
    KernelType,
    MechanismFamily,
    NeuralNetworkType,
    NoiseDistribution,
    NoiseMode,
    QueryType,
    VariableDataType,
)
from causal_profiler.space_of_interest import SpaceOfInterest


class TestSpaceOfInterest(unittest.TestCase):

    def test_default_initialization(self):
        space = SpaceOfInterest()
        self.assertEqual(space.number_of_nodes, (5, 15))
        self.assertEqual(space.variable_dimensionality, (1, 1))
        self.assertEqual(space.mechanism_family, MechanismFamily.TABULAR)
        self.assertEqual(space.mechanism_args, None)
        self.assertEqual(space.expected_edges, "N")
        self.assertIsNone(space.predefined_graph_file)
        self.assertEqual(space.number_of_noise_regions, None)
        self.assertEqual(space.number_of_categories, (2, 2))
        self.assertEqual(space.noise_distribution, NoiseDistribution.UNIFORM)
        self.assertEqual(space.noise_mode, NoiseMode.ADDITIVE)
        self.assertEqual(space.noise_args, [-1, 1])
        self.assertEqual(space.variable_type, VariableDataType.CONTINUOUS)
        self.assertEqual(space.proportion_of_hidden_variables, 0.0)
        self.assertEqual(space.number_of_queries, 1)
        self.assertEqual(space.query_type, QueryType.CTF_TE)
        self.assertIsNone(space.specific_query)
        self.assertEqual(space.number_of_data_points, 1000)
        self.assertEqual(space.kernel_type, KernelType.GAUSSIAN)
        self.assertEqual(space.kernel_bandwidth, 0.1)
        self.assertIsNone(space.kernel_fn)

    def test_number_of_nodes_range(self):
        space = SpaceOfInterest(number_of_nodes=(10, 20))
        self.assertEqual(space.number_of_nodes, (10, 20))

        # Invalid range
        with self.assertRaises(AssertionError):
            SpaceOfInterest(number_of_nodes=(0, 10))

        with self.assertRaises(AssertionError):
            SpaceOfInterest(number_of_nodes=(-1, -5))

    def test_variable_dimensionality(self):
        space = SpaceOfInterest(variable_dimensionality=(1, 5))
        self.assertEqual(space.variable_dimensionality, (1, 5))

        with self.assertRaises(AssertionError):
            SpaceOfInterest(variable_dimensionality=(0, 0))

        with self.assertRaises(AssertionError):
            SpaceOfInterest(variable_dimensionality=5)

    def test_expected_edges(self):
        space = SpaceOfInterest(expected_edges=(1, 5))
        self.assertEqual(space.expected_edges, (1, 5))

        space = SpaceOfInterest(expected_edges=2)
        self.assertEqual(space.expected_edges, 2)

        space = SpaceOfInterest(expected_edges="log(N)")
        self.assertEqual(space.expected_edges, "log(N)")

        with self.assertRaises(AssertionError):
            SpaceOfInterest(expected_edges=(4, 3))

        with self.assertRaises(AssertionError):
            SpaceOfInterest(expected_edges="")

    def test_number_of_noise_regions(self):
        space = SpaceOfInterest(
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions=(1, 5),
        )
        self.assertEqual(space.number_of_noise_regions, (1, 5))

        space = SpaceOfInterest(
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions=1,
        )
        self.assertEqual(space.number_of_noise_regions, 1)

        space = SpaceOfInterest(
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions=4,
        )
        self.assertEqual(space.number_of_noise_regions, 4)

        space = SpaceOfInterest(
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions="log(N)",
        )
        self.assertEqual(space.number_of_noise_regions, "log(N)")

        space = SpaceOfInterest(
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions=(1, "log(N)"),
        )
        self.assertEqual(space.number_of_noise_regions, (1, "log(N)"))

        with self.assertRaises(AssertionError):
            SpaceOfInterest(
                variable_type=VariableDataType.DISCRETE,
                number_of_noise_regions=(4, 3),
            )

    def test_number_of_categories(self):
        space = SpaceOfInterest(number_of_categories=(1, 5))
        self.assertEqual(space.number_of_categories, (1, 5))

        space = SpaceOfInterest(number_of_categories=2)
        self.assertEqual(space.number_of_categories, (2, 2))

        with self.assertRaises(AssertionError):
            SpaceOfInterest(number_of_categories=(4, 3))

    def test_mechanism_family(self):
        for mechanism_family in MechanismFamily:
            space = SpaceOfInterest(mechanism_family=mechanism_family)
            self.assertEqual(space.mechanism_family, mechanism_family)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(mechanism_family="unsupported")

    def test_mechanism_args(self):
        space = SpaceOfInterest(mechanism_args=[NeuralNetworkType.FEEDFORWARD, 4])
        self.assertEqual(space.mechanism_args, [NeuralNetworkType.FEEDFORWARD, 4])

        with self.assertRaises(AssertionError):
            SpaceOfInterest(mechanism_args="not_a_list")

    def test_noise_distribution(self):
        for noise_distribution in NoiseDistribution:
            space = SpaceOfInterest(noise_distribution=noise_distribution)
            self.assertEqual(space.noise_distribution, noise_distribution)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(noise_distribution="invalid_noise_distribution")

    def test_noise_mode(self):
        for noise_mode in NoiseMode:
            space = SpaceOfInterest(noise_mode=noise_mode)
            self.assertEqual(space.noise_mode, noise_mode)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(noise_mode="invalid_noise_mode")

    def test_noise_args(self):
        space = SpaceOfInterest(noise_args=[0, 1])
        self.assertEqual(space.noise_args, [0, 1])

        with self.assertRaises(AssertionError):
            SpaceOfInterest(noise_args=[1])

    def test_proportion_of_hidden_variables_range(self):
        # Needs to be in [0.0, 1.0]
        with self.assertRaises(AssertionError):
            SpaceOfInterest(proportion_of_hidden_variables=1.4)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(proportion_of_hidden_variables=-0.1)

        space = SpaceOfInterest(proportion_of_hidden_variables=0.6)
        self.assertEqual(space.proportion_of_hidden_variables, 0.6)

    def test_query_type(self):
        for query_type in QueryType:
            space = SpaceOfInterest(query_type=query_type)
            self.assertEqual(space.query_type, query_type)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(query_type="invalid_query")

    def test_specific_query(self):
        space = SpaceOfInterest(specific_query="query_string")
        self.assertEqual(space.specific_query, "query_string")

        space = SpaceOfInterest(specific_query=None)
        self.assertIsNone(space.specific_query)

    def test_number_of_data_points(self):
        space = SpaceOfInterest(number_of_data_points=10)
        self.assertEqual(space.number_of_data_points, 10)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(number_of_data_points=0)

    def test_kernel_type(self):
        for kernel_type in KernelType:
            space = SpaceOfInterest(kernel_type=kernel_type)
            self.assertEqual(space.kernel_type, kernel_type)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(kernel_type="invalid_kernel_type")

    def test_kernel_bandwidth(self):
        space = SpaceOfInterest(kernel_bandwidth=0.5)
        self.assertEqual(space.kernel_bandwidth, 0.5)

        space = SpaceOfInterest(kernel_bandwidth=2)
        self.assertEqual(space.kernel_bandwidth, 2)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(kernel_bandwidth="not_a_number")

    def test_kernel_fn(self):
        # Test with None (default)
        space = SpaceOfInterest(kernel_fn=None)
        self.assertIsNone(space.kernel_fn)
        self.assertEqual(space.kernel_type, KernelType.GAUSSIAN)

        # Test with a callable
        def custom_kernel(x, target, bandwidth):
            return 1.0

        space = SpaceOfInterest(kernel_fn=custom_kernel)
        self.assertEqual(space.kernel_fn, custom_kernel)
        self.assertEqual(space.kernel_type, KernelType.CUSTOM)

        space = SpaceOfInterest(kernel_fn=custom_kernel, kernel_type=KernelType.UNIFORM)
        self.assertEqual(space.kernel_fn, custom_kernel)
        self.assertEqual(space.kernel_type, KernelType.CUSTOM)

        # Test with non-callable
        with self.assertRaises(AssertionError):
            SpaceOfInterest(kernel_fn="not_a_callable")

    def test_file_save_and_load(self):
        filename = "test_space_config.json"

        space = SpaceOfInterest(
            number_of_nodes=(8, 12),
            variable_dimensionality=(2, 2),
            mechanism_family=MechanismFamily.NEURAL_NETWORK,
            mechanism_args=[NeuralNetworkType.RNN, 8],
            expected_edges="log(N)",
            predefined_graph_file=None,
            number_of_categories=(1, 5),
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_mode=NoiseMode.MULTIPLICATIVE,
            number_of_noise_regions=(1, "N"),
            noise_args=[0, 1],
            variable_type=VariableDataType.DISCRETE,
            proportion_of_hidden_variables=0.5,
            number_of_queries=3,
            query_type=QueryType.ATE,
            specific_query="query_example",
            number_of_data_points=500,
            kernel_type=KernelType.UNIFORM,
            kernel_bandwidth=0.25,
            # Note: We cannot save/load a custom function directly,
            # as it's not JSON serializable
        )

        space.save_to_file(filename)
        loaded_space = SpaceOfInterest.load_from_file(filename)

        # Check all attributes match
        self.assertEqual(loaded_space.number_of_nodes, (8, 12))
        self.assertEqual(loaded_space.variable_dimensionality, (2, 2))
        self.assertEqual(loaded_space.mechanism_family, MechanismFamily.NEURAL_NETWORK)
        self.assertEqual(loaded_space.mechanism_args, [NeuralNetworkType.RNN.value, 8])
        self.assertEqual(loaded_space.expected_edges, "log(N)")
        self.assertIsNone(loaded_space.predefined_graph_file)
        self.assertEqual(loaded_space.number_of_categories, (1, 5))
        self.assertEqual(loaded_space.noise_distribution, NoiseDistribution.GAUSSIAN)
        self.assertEqual(loaded_space.noise_mode, NoiseMode.MULTIPLICATIVE)
        self.assertEqual(loaded_space.number_of_noise_regions, (1, "N"))
        self.assertEqual(loaded_space.noise_args, [0, 1])
        self.assertEqual(loaded_space.variable_type, VariableDataType.DISCRETE)
        self.assertEqual(loaded_space.proportion_of_hidden_variables, 0.5)
        self.assertEqual(loaded_space.number_of_queries, 3)
        self.assertEqual(loaded_space.query_type, QueryType.ATE)
        self.assertEqual(loaded_space.specific_query, "query_example")
        self.assertEqual(loaded_space.number_of_data_points, 500)
        self.assertEqual(loaded_space.kernel_type, KernelType.UNIFORM)
        self.assertEqual(loaded_space.kernel_bandwidth, 0.25)
        self.assertIsNone(loaded_space.kernel_fn)  # Function won't be preserved in JSON

        # Clean up
        os.remove(filename)

    def test_kernel_save_load(self):
        """Test specifically for kernel parameters serialization and deserialization"""
        filename = "test_kernel_config.json"

        for kernel_type in KernelType:
            # Create space with specific kernel settings
            original_space = SpaceOfInterest(
                kernel_type=kernel_type, kernel_bandwidth=0.42
            )

            # Save to file
            original_space.save_to_file(filename)

            # Load from file
            loaded_space = SpaceOfInterest.load_from_file(filename)

            # Check that kernel settings are preserved
            self.assertEqual(loaded_space.kernel_type, kernel_type)
            self.assertEqual(loaded_space.kernel_bandwidth, 0.42)

        # Clean up
        os.remove(filename)

    def test_invalid_filename(self):
        with self.assertRaises(FileNotFoundError):
            SpaceOfInterest.load_from_file("non_existent_file.json")

    def test_discrete_function_sampling(self):
        # Test default value
        space = SpaceOfInterest()
        self.assertEqual(
            space.discrete_function_sampling, FunctionSampling.SAMPLE_REJECTION
        )

        # Test with each possible value
        for function_sampling in FunctionSampling:
            space = SpaceOfInterest(discrete_function_sampling=function_sampling)
            self.assertEqual(space.discrete_function_sampling, function_sampling)

        # Test with invalid value
        with self.assertRaises(AssertionError):
            SpaceOfInterest(discrete_function_sampling="invalid_function_sampling")

    def test_discrete_function_sampling_save_load(self):
        # Test that discrete_function_sampling is correctly saved and loaded
        filename = "test_function_sampling.json"

        for function_sampling in FunctionSampling:
            # Create a SpaceOfInterest with a specific function_sampling
            original_space = SpaceOfInterest(
                discrete_function_sampling=function_sampling
            )

            # Save to file
            original_space.save_to_file(filename)

            # Load from file
            loaded_space = SpaceOfInterest.load_from_file(filename)

            # Check that the function_sampling is preserved
            self.assertEqual(loaded_space.discrete_function_sampling, function_sampling)

        # Clean up
        os.remove(filename)

    def test_allow_nan_queries_validation(self):
        """Test that allow_nan_queries parameter validation works correctly."""
        # Default should be False
        space = SpaceOfInterest()
        self.assertFalse(space.allow_nan_queries)

        # Valid boolean values should work
        space_true = SpaceOfInterest(allow_nan_queries=True)
        self.assertTrue(space_true.allow_nan_queries)

        space_false = SpaceOfInterest(allow_nan_queries=False)
        self.assertFalse(space_false.allow_nan_queries)

        # Invalid values should raise AssertionError
        with self.assertRaises(AssertionError):
            SpaceOfInterest(allow_nan_queries="invalid")

        with self.assertRaises(AssertionError):
            SpaceOfInterest(allow_nan_queries=123)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(allow_nan_queries=None)

    def test_allow_nan_queries_in_to_dict(self):
        """Test that allow_nan_queries is included in to_dict serialization."""
        space_true = SpaceOfInterest(allow_nan_queries=True)
        space_false = SpaceOfInterest(allow_nan_queries=False)

        dict_true = space_true.to_dict()
        dict_false = space_false.to_dict()

        self.assertIn("allow_nan_queries", dict_true)
        self.assertIn("allow_nan_queries", dict_false)
        self.assertTrue(dict_true["allow_nan_queries"])
        self.assertFalse(dict_false["allow_nan_queries"])

    def test_allow_nan_queries_save_load(self):
        """Test that allow_nan_queries is properly saved and loaded from file."""
        filename = "test_allow_nan_queries.json"

        for allow_nan_value in [True, False]:
            # Create space with specific allow_nan_queries setting
            original_space = SpaceOfInterest(allow_nan_queries=allow_nan_value)

            # Save to file
            original_space.save_to_file(filename)

            # Load from file
            loaded_space = SpaceOfInterest.load_from_file(filename)

            # Check that allow_nan_queries is preserved
            self.assertEqual(loaded_space.allow_nan_queries, allow_nan_value)

        # Clean up
        os.remove(filename)

    def test_disable_query_sampling_validation(self):
        """Test that disable_query_sampling parameter validation works correctly."""
        # Default should be False
        space = SpaceOfInterest()
        self.assertFalse(space.disable_query_sampling)

        # Valid boolean values should work
        space_true = SpaceOfInterest(disable_query_sampling=True)
        self.assertTrue(space_true.disable_query_sampling)

        space_false = SpaceOfInterest(disable_query_sampling=False)
        self.assertFalse(space_false.disable_query_sampling)

        # Invalid values should raise AssertionError
        with self.assertRaises(AssertionError):
            SpaceOfInterest(disable_query_sampling="invalid")

        with self.assertRaises(AssertionError):
            SpaceOfInterest(disable_query_sampling=123)

        with self.assertRaises(AssertionError):
            SpaceOfInterest(disable_query_sampling=None)

    def test_disable_query_sampling_in_to_dict(self):
        """Test that disable_query_sampling is included in to_dict serialization."""
        space_true = SpaceOfInterest(disable_query_sampling=True)
        space_false = SpaceOfInterest(disable_query_sampling=False)

        dict_true = space_true.to_dict()
        dict_false = space_false.to_dict()

        self.assertIn("disable_query_sampling", dict_true)
        self.assertIn("disable_query_sampling", dict_false)
        self.assertTrue(dict_true["disable_query_sampling"])
        self.assertFalse(dict_false["disable_query_sampling"])

    def test_disable_query_sampling_save_load(self):
        """Test that disable_query_sampling is properly saved and loaded from file."""
        filename = "test_disable_query_sampling.json"

        for disable_query_sampling_value in [True, False]:
            # Create space with specific disable_query_sampling setting
            original_space = SpaceOfInterest(
                disable_query_sampling=disable_query_sampling_value
            )

            # Save to file
            original_space.save_to_file(filename)

            # Load from file
            loaded_space = SpaceOfInterest.load_from_file(filename)

            # Check that disable_query_sampling is preserved
            self.assertEqual(
                loaded_space.disable_query_sampling, disable_query_sampling_value
            )

        # Clean up
        os.remove(filename)

    def test_unsupported_fields_warning(self):
        """Test that any unsupported fields trigger appropriate warnings."""

        # Test that any extra fields trigger warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            SpaceOfInterest(
                markovian=True,
                semi_markovian=False,
                control_positivity=True,
                causal_graph="test.json",
            )

            # Should have triggered one warning
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, UserWarning))
            warning_msg = str(w[0].message)

            # Check that all unsupported fields are mentioned
            self.assertIn("markovian", warning_msg)
            self.assertIn("semi_markovian", warning_msg)
            self.assertIn("control_positivity", warning_msg)
            self.assertIn("causal_graph", warning_msg)

    def test_no_warning_for_valid_fields(self):
        """Test that valid fields don't trigger warnings."""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            SpaceOfInterest(
                number_of_nodes=(3, 8),
                variable_type=VariableDataType.DISCRETE,
                number_of_queries=5,
            )

            # Should not have triggered any warnings
            self.assertEqual(len(w), 0)


if __name__ == "__main__":
    unittest.main()
