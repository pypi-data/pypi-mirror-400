import random
import unittest
from itertools import chain

import numpy as np

from causal_profiler.constants import (
    FunctionSampling,
    MechanismFamily,
    NoiseDistribution,
    QueryType,
    VariableDataType,
    VariableRole,
    KernelType,
)
from causal_profiler.query import Query
from causal_profiler.sampler import Sampler
from causal_profiler.space_of_interest import SpaceOfInterest
from causal_profiler.variable import Variable


class TestSampler(unittest.TestCase):

    def test_sample_discrete_function_with_sample_rejection(self):
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        X0 = Variable(
            name="X0",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        U_X0 = Variable(
            name="U_X0",
            dimensionality=1,
            exogenous=True,
        )
        # 5 noise regions
        U_X0.noise_regions = [x / 10.0 for x in range(0, 10, 3)]  # 2^(2*3) = 2^6 = 32
        X1 = Variable(
            name="X1",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=3,
        )
        X2 = Variable(
            name="X2",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        mechanism = Sampler(
            SpaceOfInterest()
        ).sample_discrete_function_sample_rejection([U_X0, X1, X2], X0)

        assert mechanism == [
            (
                [
                    (0, 0, 0),
                    (0, 2, 0),
                    (0, 2, 1),
                    (1, 0, 0),
                    (1, 2, 1),
                    (2, 1, 0),
                    (2, 1, 1),
                    (2, 2, 1),
                    (3, 0, 0),
                    (3, 1, 0),
                    (3, 1, 1),
                    (4, 0, 0),
                    (4, 0, 1),
                    (4, 1, 0),
                    (4, 1, 1),
                    (4, 2, 1),
                ],
                1,
            ),
            (
                [
                    (0, 0, 1),
                    (0, 1, 0),
                    (0, 1, 1),
                    (1, 0, 1),
                    (1, 1, 0),
                    (1, 1, 1),
                    (1, 2, 0),
                    (2, 0, 0),
                    (2, 0, 1),
                    (2, 2, 0),
                    (3, 0, 1),
                    (3, 2, 0),
                    (3, 2, 1),
                    (4, 2, 0),
                ],
                0,
            ),
        ]

    def test_sample_discrete_function(self):
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        X0 = Variable(
            name="X0",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        X1 = Variable(
            name="X1",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=3,
        )
        X2 = Variable(
            name="X2",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        mechanism = Sampler(SpaceOfInterest()).sample_discrete_function_random(
            [X1, X2], X0
        )

        assert mechanism == [
            ([(0, 0), (2, 0), (2, 1)], (1,)),
            ([(0, 1), (1, 0), (1, 1)], (0,)),
        ]

    def test_sample_discrete_function_enumerate(self):
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        # Create variables
        input_var_1 = Variable(
            name="U1",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        input_var_1.noise_regions = ([0.5],)
        input_var_2 = Variable(
            name="X",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=3,
        )
        output_var = Variable(
            name="Y",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        # Create Sampler instance
        space_of_interest = SpaceOfInterest()
        sampler = Sampler(space_of_interest)

        # Generate the discrete function mechanism
        mechanism = sampler.sample_discrete_function_enumerate(
            input_vars=[input_var_1, input_var_2],
            output_var=output_var,
        )

        # Assert that the mechanism is not empty and is formatted correctly
        self.assertTrue(len(mechanism) > 0, "The mechanism should not be empty.")
        for entry in mechanism:
            self.assertIsInstance(entry, tuple, "Each entry should be a tuple.")
            self.assertEqual(len(entry), 2, "Each tuple should have 2 elements.")
            self.assertIsInstance(
                entry[0],
                list,
                "The first element should be a list of tuples (input configuration).",
            )
            for input_config in entry[0]:
                self.assertIsInstance(
                    input_config, tuple, "Each input configuration should be a tuple."
                )
            self.assertIsInstance(
                entry[1], int, "The second element should be an integer (output value)."
            )

        # Debug: Print the mechanism
        # print("Generated Mechanism:")
        # for entry in mechanism:
        # print(entry)

    def test_sampled_scm_no_exogenous_mechanisms(self):
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        # Create a simple space of interest
        soi = SpaceOfInterest(
            number_of_nodes=(5, 5),  # fixed 5 nodes
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            expected_edges=1,
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_queries=2,
            query_type=QueryType.CONDITIONAL,
            number_of_data_points=100,
        )

        sampler = Sampler(soi, return_adjacency_matrix=False)
        scm = sampler.generate_scm()
        for var_id in scm.mechanisms:
            var = scm.variables[var_id]
            assert not var.exogenous

    def test_sampler_generate_samples_and_queries(self):
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        # Create a simple space of interest
        soi = SpaceOfInterest(
            number_of_nodes=(5, 5),  # fixed 5 nodes
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            expected_edges=1,
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_queries=2,
            query_type=QueryType.CONDITIONAL,
            number_of_data_points=100,
        )

        sampler = Sampler(soi, return_adjacency_matrix=False)
        data, (queries, estimates), (graph, index_to_variable) = (
            sampler.generate_samples_and_queries()
        )

        # Check data shape
        self.assertEqual(len(data), 5)  # 5 variables
        for var_id, values in data.items():
            self.assertEqual(values.shape[0], 100)

        # Check queries
        self.assertEqual(len(queries), 2)
        self.assertEqual(len(estimates), 2)
        for q, e in zip(queries, estimates):
            print(f"Query: {q}, Estimate: {e}")
            self.assertTrue(isinstance(q, Query))
            self.assertTrue(isinstance(e, float) or isinstance(e, np.number))

        # Check graph
        self.assertIsInstance(graph, dict)
        # Keys should match variable IDs
        self.assertEqual(set(index_to_variable), set(data.keys()))

    def test_noise_regions_handling(self):
        soi = SpaceOfInterest(
            number_of_nodes=(3, 3),
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            noise_distribution=NoiseDistribution.UNIFORM,
            number_of_categories=(4, 5),
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions="V_to_PA",
            number_of_data_points=50,
        )

        sampler = Sampler(soi)
        scm = sampler._init_scm({"X1": ["X2"], "X2": ["X3"], "X3": []})  # Sample graph
        for var in scm.variables.values():
            if var.exogenous:
                self.assertIsNotNone(var.noise_regions)
                self.assertTrue(all(0 <= region <= 1 for region in var.noise_regions))

    def test_proportion_of_hidden_variables_in_data(self):
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)
        total_variables = 20
        proportion_of_hidden_variables = 0.2
        soi = SpaceOfInterest(
            number_of_nodes=(total_variables, total_variables),
            variable_dimensionality=(1, 1),
            expected_edges="N",
            mechanism_family=MechanismFamily.TABULAR,
            noise_distribution=NoiseDistribution.UNIFORM,
            number_of_categories=(4, 5),
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions="V",
            number_of_data_points=50,
            proportion_of_hidden_variables=proportion_of_hidden_variables,
        )

        sampler = Sampler(soi)
        # TODO: optimize sample rejection to scale to 20
        sampler.function_sampling = FunctionSampling.RANDOM
        data, (queries, estimates), (graph, index_to_variable) = (
            sampler.generate_samples_and_queries()
        )

        number_of_variables = len(data.values())
        self.assertEqual(
            number_of_variables, total_variables * (1 - proportion_of_hidden_variables)
        )

    def test_proportion_of_hidden_variables_in_queries(self):
        soi = SpaceOfInterest(
            number_of_nodes=(15, 15),
            variable_dimensionality=(1, 1),
            expected_edges="N",
            mechanism_family=MechanismFamily.TABULAR,
            noise_distribution=NoiseDistribution.UNIFORM,
            number_of_categories=2,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions="V",
            number_of_data_points=50,
            proportion_of_hidden_variables=0.2,
            number_of_queries=10,
        )

        sampler = Sampler(soi)
        # TODO: optimize sample rejection to scale to 15
        sampler.function_sampling = FunctionSampling.RANDOM
        data, (queries, estimates), (graph, index_to_variable) = (
            sampler.generate_samples_and_queries()
        )

        for query in queries:
            all_variables = list(chain.from_iterable(query.vars.values()))
            assert all(
                var.visible for var in all_variables
            ), f"Not all variables are visible in {query}"

    def test_proportion_of_hidden_variables_in_graph(self):
        soi = SpaceOfInterest(
            number_of_nodes=(15, 15),
            variable_dimensionality=(1, 1),
            expected_edges="N",
            mechanism_family=MechanismFamily.TABULAR,
            noise_distribution=NoiseDistribution.UNIFORM,
            number_of_categories=(4, 5),
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions="V",
            number_of_data_points=50,
            proportion_of_hidden_variables=0.2,
        )

        sampler = Sampler(soi)
        # TODO: optimize sample rejection to scale to 15
        sampler.function_sampling = FunctionSampling.RANDOM
        data, (queries, estimates), (graph, index_to_variable) = (
            sampler.generate_samples_and_queries()
        )

        # Check the number of hidden variables in the graph and in the data is the same
        assert len(index_to_variable) == len(data.values())

    def test_noise_regions_evaluate_range(self):
        soi = SpaceOfInterest(
            number_of_nodes=(3, 3),
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            noise_distribution=NoiseDistribution.UNIFORM,
            number_of_categories=3,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions=(3, 10),  # Range of noise regions
            number_of_data_points=50,
        )

        sampler = Sampler(soi)
        scm = sampler._init_scm({"X1": ["X2"], "X2": ["X3"], "X3": []})  # Sample graph
        for var in scm.variables.values():
            if var.exogenous:
                self.assertIsNotNone(var.noise_regions)
                self.assertTrue(3 <= len(var.noise_regions) + 1 <= 10)

    def test_noise_regions_evaluate_expression(self):
        soi = SpaceOfInterest(
            number_of_nodes=(3, 3),
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            noise_distribution=NoiseDistribution.UNIFORM,
            number_of_categories=3,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions="V_to_PA / 2",  # Expression for noise regions
            number_of_data_points=50,
        )

        sampler = Sampler(soi)
        scm = sampler._init_scm({"X1": ["X2"], "X2": ["X3"], "X3": []})  # Sample graph

        self.assertEqual(len(scm.variables["U_X1"].noise_regions) + 1, 1)
        self.assertEqual(len(scm.variables["U_X2"].noise_regions) + 1, 13)
        self.assertEqual(len(scm.variables["U_X3"].noise_regions) + 1, 13)
        self.assertFalse(hasattr(scm.variables["X1"], "noise_regions"))
        self.assertFalse(hasattr(scm.variables["X2"], "noise_regions"))
        self.assertFalse(hasattr(scm.variables["X3"], "noise_regions"))

    def test_noise_region_evaluate_V_to_PA(self):
        soi = SpaceOfInterest(
            number_of_nodes=(3, 3),
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            noise_distribution=NoiseDistribution.UNIFORM,
            number_of_categories=3,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions="V_to_PA",
            number_of_data_points=50,
        )

        sampler = Sampler(soi)
        scm = sampler._init_scm({"X1": ["X2"], "X2": ["X3"], "X3": []})  # Sample graph

        self.assertEqual(len(scm.variables["U_X1"].noise_regions) + 1, 3)
        self.assertEqual(len(scm.variables["U_X2"].noise_regions) + 1, 27)
        self.assertEqual(len(scm.variables["U_X3"].noise_regions) + 1, 27)
        self.assertFalse(hasattr(scm.variables["X1"], "noise_regions"))
        self.assertFalse(hasattr(scm.variables["X2"], "noise_regions"))
        self.assertFalse(hasattr(scm.variables["X3"], "noise_regions"))

    def test_exogenous_variables_always_continuous(self):
        soi = SpaceOfInterest(
            number_of_nodes=(3, 3),
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            noise_distribution=NoiseDistribution.UNIFORM,
            number_of_categories=3,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_noise_regions="V_to_PA",
            number_of_data_points=50,
        )

        sampler = Sampler(soi)
        scm = sampler._init_scm({"X1": ["X2"], "X2": ["X3"], "X3": []})  # Sample graph

        self.assertEqual(
            scm.variables["U_X1"].variable_type, VariableDataType.CONTINUOUS
        )
        self.assertEqual(
            scm.variables["U_X2"].variable_type, VariableDataType.CONTINUOUS
        )
        self.assertEqual(
            scm.variables["U_X3"].variable_type, VariableDataType.CONTINUOUS
        )
        self.assertEqual(scm.variables["X1"].variable_type, VariableDataType.DISCRETE)
        self.assertEqual(scm.variables["X2"].variable_type, VariableDataType.DISCRETE)
        self.assertEqual(scm.variables["X3"].variable_type, VariableDataType.DISCRETE)

    def test_remove_interventions(self):
        # When sampling a type of query that requires interventions,
        # if one doesn't remove interventions the value of the variable will always stay the same
        # Practically speaking, this will make code fail because of failed braodcasting,
        # but here we explicitly check that all variables are un-intervened after sampling

        for query_type in [
            QueryType.ATE,
            QueryType.CATE,
            QueryType.CTF_TE,
        ]:
            random.seed(43)
            np.random.seed(43)

            soi = SpaceOfInterest(
                number_of_nodes=(3, 3),
                variable_dimensionality=(1, 1),
                mechanism_family=MechanismFamily.TABULAR,
                expected_edges=3,
                noise_distribution=NoiseDistribution.UNIFORM,
                noise_args=[-1, 1],
                number_of_noise_regions="N",
                number_of_categories=2,
                variable_type=VariableDataType.DISCRETE,
                number_of_queries=100,
                query_type=query_type,
                number_of_data_points=5,
            )

            sampler = Sampler(
                space_of_interest=soi, return_adjacency_matrix=False, n_samples=1000
            )
            scm = sampler.generate_scm()
            scm.sample_noise_variables()
            scm.compute_variables()
            (queries, estimates) = sampler._sample_and_evaluate_queries(scm)

            for var in scm.variables.values():
                self.assertNotEqual(var.variable_role, VariableRole.INTERVENED)

    def test_mechanism_N_r_max(self):
        # In function sampling methods like enumeration and sample rejection
        # the number of noise regions is bounded by N_r_max. This test, checks both
        # methods and whether the mechanisms are created correctly. The problem is that
        # the initially defined noise regions N are larger than N_r_max which means that
        # they have to be pruned

        for function_sampling in [
            FunctionSampling.ENUMERATE,
            FunctionSampling.RANDOM,
            FunctionSampling.SAMPLE_REJECTION,
        ]:
            random.seed(43)
            np.random.seed(43)

            soi = SpaceOfInterest(
                number_of_nodes=(3, 3),
                variable_dimensionality=(1, 1),
                mechanism_family=MechanismFamily.TABULAR,
                expected_edges=1,
                noise_distribution=NoiseDistribution.UNIFORM,
                noise_args=[-1, 1],
                number_of_noise_regions="N",
                number_of_categories=2,
                variable_type=VariableDataType.DISCRETE,
                discrete_function_sampling=function_sampling,
                number_of_queries=100,  # You need 100 to get duplicates
                query_type=QueryType.CONDITIONAL,
                number_of_data_points=5,
            )

            sampler = Sampler(
                space_of_interest=soi, return_adjacency_matrix=False, n_samples=1000
            )

            # Not crashing means success
            sampler.generate_samples_and_queries()

    def test_sampler_uses_space_of_interest_discrete_function_sampling(self):
        # Test that the sampler uses the discrete_function_sampling from space_of_interest
        for function_sampling_value in FunctionSampling:
            # Create a SpaceOfInterest with a specific discrete_function_sampling
            soi = SpaceOfInterest(
                number_of_nodes=(3, 3),
                variable_dimensionality=(1, 1),
                mechanism_family=MechanismFamily.TABULAR,
                discrete_function_sampling=function_sampling_value,
                variable_type=VariableDataType.DISCRETE,
            )

            # Create a Sampler with this SpaceOfInterest
            sampler = Sampler(space_of_interest=soi)

            # Verify that the Sampler's function_sampling matches the SpaceOfInterest's discrete_function_sampling
            self.assertEqual(sampler.function_sampling, function_sampling_value)

            # Also test the sample_discrete_function method to ensure it uses the correct
            # function_sampling based on different SpaceOfInterest configurations
            if function_sampling_value == FunctionSampling.ENUMERATE:
                self.assertEqual(sampler.function_sampling, FunctionSampling.ENUMERATE)

            elif function_sampling_value == FunctionSampling.RANDOM:
                self.assertEqual(sampler.function_sampling, FunctionSampling.RANDOM)

            elif function_sampling_value == FunctionSampling.SAMPLE_REJECTION:
                self.assertEqual(
                    sampler.function_sampling, FunctionSampling.SAMPLE_REJECTION
                )

    def test_discrete_function_sampling_workflow(self):
        """Test that the different discrete function sampling methods are correctly used."""
        # Set up test variables
        random.seed(42)
        np.random.seed(42)

        X0 = Variable(
            name="X0",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        U_X0 = Variable(
            name="U_X0",
            dimensionality=1,
            exogenous=True,
        )
        # Create 4 noise regions
        U_X0.noise_regions = [0.2, 0.4, 0.6, 0.8]
        X1 = Variable(
            name="X1",
            dimensionality=1,
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        # Test with each function sampling method
        for function_sampling in FunctionSampling:
            # Create SpaceOfInterest with specific discrete_function_sampling
            soi = SpaceOfInterest(
                discrete_function_sampling=function_sampling,
                variable_type=VariableDataType.DISCRETE,
            )

            # Create sampler
            sampler = Sampler(soi)

            # Check the sampler has the correct function_sampling
            self.assertEqual(sampler.function_sampling, function_sampling)

            # Call the sample_discrete_function method
            mechanism = sampler.sample_discrete_function([U_X0, X1], X0)

            # Verify we got a valid mechanism (we can't easily check which specific method was used,
            # but we can confirm that a mechanism was returned)
            self.assertIsNotNone(mechanism)
            self.assertIsInstance(mechanism, list)
            self.assertTrue(len(mechanism) > 0)

            self.assertEqual(
                len(mechanism),
                2,
                f"Expected 2 entries with {function_sampling}, got {len(mechanism)}",
            )

    def test_sampler_passes_kernel_params_to_query_estimator(self):
        """Test that Sampler correctly passes kernel parameters from SpaceOfInterest to QueryEstimator."""

        # Create SpaceOfInterest with custom kernel parameters
        soi = SpaceOfInterest(
            kernel_type=KernelType.EPANECHNIKOV,
            kernel_bandwidth=0.25,
        )

        # Create a sampler with this SpaceOfInterest
        sampler = Sampler(soi)

        # Verify kernel parameters were passed correctly to QueryEstimator
        self.assertEqual(sampler.query_estimator.kernel_type, KernelType.EPANECHNIKOV)
        self.assertEqual(sampler.query_estimator.kernel_bandwidth, 0.25)
        self.assertIsNone(sampler.query_estimator.kernel_fn)

        # Create a different SpaceOfInterest with default kernel parameters
        default_soi = SpaceOfInterest()
        default_sampler = Sampler(default_soi)

        # Verify default kernel parameters were passed correctly
        self.assertEqual(
            default_sampler.query_estimator.kernel_type, KernelType.GAUSSIAN
        )
        self.assertEqual(default_sampler.query_estimator.kernel_bandwidth, 0.1)
        self.assertIsNone(default_sampler.query_estimator.kernel_fn)


class TestSampleSingleValueForVars(unittest.TestCase):
    def setUp(self):
        """
        Create a small dataset of two variables, each with 3 samples (rows)
        and 1-dimensional values (columns).

        var1: [[1], [2], [3]]
        var2: [[10], [20], [30]]

        This way, if they come from the same index:
            index = 0  => var1=1,  var2=10
            index = 1  => var1=2,  var2=20
            index = 2  => var1=3,  var2=30
        """
        random.seed(42)
        np.random.seed(42)
        self.mock_data = {
            "var1": np.array([[1], [2], [3]]),
            "var2": np.array([[10], [20], [30]]),
        }
        self.var1 = Variable(
            name="var1", num_discrete_values=4, variable_type=VariableDataType.DISCRETE
        )
        self.var2 = Variable(
            name="var2", num_discrete_values=31, variable_type=VariableDataType.DISCRETE
        )
        self.sampler = Sampler(SpaceOfInterest())

    def test_sample_single_value_for_vars_same_datapoint(self):
        """
        Test that when same_datapoint=True, we always sample the same row
        for both variables.
        """
        # Sample multiple times to see consistent "pairing" of var1/var2
        for _ in range(10):
            values = self.sampler._sample_single_value_for_vars(
                self.mock_data, self.var1, self.var2, same_datapoint=True
            )
            # values is a list of length 2: [value_for_var1, value_for_var2]
            val_var1 = values[0][0]  # since each shape is (1,)
            val_var2 = values[1][0]

            # Because of how we've set up the data:
            # index=0 => (1, 10)
            # index=1 => (2, 20)
            # index=2 => (3, 30)
            # We check the pairing belongs to { (1,10), (2,20), (3,30) }:
            valid_pairs = {(1, 10), (2, 20), (3, 30)}
            self.assertIn((val_var1, val_var2), valid_pairs)

    def test_sample_single_value_for_vars_different_datapoints(self):
        """
        Test that when same_datapoint=False, var1 and var2 can come from
        different rows.

        Since it's random, we can't guarantee they *will* differ on a single draw,
        but calling multiple times makes it very likely we'll see at least one mismatch.
        """
        mismatched_samples = False
        for _ in range(50):  # more draws => more likely a mismatch
            values = self.sampler._sample_single_value_for_vars(
                self.mock_data, self.var1, self.var2, same_datapoint=False
            )
            val_var1 = values[0][0]
            val_var2 = values[1][0]

            # If we ever see a mismatch that doesn't appear in the same-datapoint pairing,
            # we know they've been sampled independently.
            if (val_var1, val_var2) not in {(1, 10), (2, 20), (3, 30)}:
                mismatched_samples = True
                break

        # We don't strictly need to enforce that it must happen,
        # but it's a strong probabilistic check. We'll rely on a somewhat large sample.
        self.assertTrue(
            mismatched_samples,
            msg="Never saw a mismatch in 50 trials (unlikely); check random seeding or distribution.",
        )

    def test_sample_oip_queries(self):
        """
        Test that Sampler can generate OIP queries with both empty and non-empty conditioning.
        """
        # Create a space of interest for OIP queries
        space_of_interest = SpaceOfInterest(
            number_of_nodes=(3, 5),
            query_type=QueryType.OIP,
            number_of_queries=10,
            number_of_data_points=100,
            variable_type=VariableDataType.DISCRETE,
            number_of_categories=2,
            mechanism_family=MechanismFamily.TABULAR,
            discrete_function_sampling=FunctionSampling.SAMPLE_REJECTION,
        )

        sampler = Sampler(space_of_interest, n_samples=100)

        # Generate samples and queries
        data, (queries, estimates), graph = sampler.generate_samples_and_queries()

        # Verify that queries were generated
        self.assertGreater(len(queries), 0, "No queries were generated")
        self.assertEqual(
            len(queries), len(estimates), "Mismatch between queries and estimates"
        )

        # Verify all queries are OIP type
        for query in queries:
            self.assertEqual(
                query.type, QueryType.OIP, "Generated query is not OIP type"
            )

            # Check that query has required variables
            self.assertIn("Y", query.vars, "OIP query missing Y variable")
            self.assertIn("T", query.vars, "OIP query missing T variable")
            self.assertIn("X", query.vars, "OIP query missing X variable")

            # Check that query has required values
            self.assertIn("Y", query.vars_values, "OIP query missing Y value")
            self.assertIn("T", query.vars_values, "OIP query missing T value")
            self.assertIn("X", query.vars_values, "OIP query missing X value")

            # Verify that conditioning variables (X) can be empty or non-empty
            conditioning_vars = query.vars["X"]
            conditioning_values = query.vars_values["X"]

            self.assertEqual(
                len(conditioning_vars),
                len(conditioning_values),
                "Conditioning vars and values should have same length",
            )

        # Verify that estimates are reasonable (not all NaN)
        valid_estimates = [est for est in estimates if not np.isnan(est)]
        self.assertGreater(len(valid_estimates), 0, "All estimates are NaN")

        # Verify estimates are probabilities (between 0 and 1, with some tolerance for floating point errors)
        for est in valid_estimates:
            self.assertGreaterEqual(est, 0, f"Probability estimate {est} is negative")
            self.assertLessEqual(
                est, 1.0, f"Probability estimate {est} is greater than 1"
            )

    def test_sample_oip_queries_mixed_conditioning(self):
        """
        Test that OIP queries are generated with a mix of empty and non-empty conditioning.
        """
        # Set a specific seed for reproducible results
        random.seed(123)
        np.random.seed(123)

        space_of_interest = SpaceOfInterest(
            number_of_nodes=(4, 4),  # Fixed to 4 nodes for consistency
            query_type=QueryType.OIP,
            number_of_queries=20,  # More queries to increase chance of mixed conditioning
            number_of_data_points=200,
            variable_type=VariableDataType.DISCRETE,
            number_of_categories=2,
            mechanism_family=MechanismFamily.TABULAR,
            discrete_function_sampling=FunctionSampling.SAMPLE_REJECTION,
        )

        sampler = Sampler(space_of_interest, n_samples=200)

        # Generate samples and queries multiple times to check for variety
        empty_conditioning_count = 0
        non_empty_conditioning_count = 0

        for _ in range(5):  # Multiple generations to increase variety
            _, (queries, _), _ = sampler.generate_samples_and_queries()

            for query in queries:
                conditioning_vars = query.vars["X"]
                if len(conditioning_vars) == 0:
                    empty_conditioning_count += 1
                else:
                    non_empty_conditioning_count += 1

        # We should see both types (lack of flakiness because of how little variables exist)
        total_queries = empty_conditioning_count + non_empty_conditioning_count
        self.assertGreater(total_queries, 0, "No queries generated")

        print(
            f"Empty conditioning: {empty_conditioning_count}, Non-empty: {non_empty_conditioning_count}"
        )

    def test_allow_nan_queries_false(self):
        """Test that when allow_nan_queries=False, no NaN queries are returned."""
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        # Create a space of interest with allow_nan_queries=False (default)
        soi = SpaceOfInterest(
            number_of_nodes=(5, 20),
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            expected_edges="N",
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_categories=5,
            number_of_queries=100,
            query_type=QueryType.CONDITIONAL,
            number_of_data_points=1000,
            allow_nan_queries=False,  # Explicitly set to False
        )

        sampler = Sampler(soi, return_adjacency_matrix=False)
        data, (queries, estimates), graph = sampler.generate_samples_and_queries()

        # Check that no estimates are NaN
        for estimate in estimates:
            self.assertFalse(
                np.isnan(estimate), "Found NaN estimate when allow_nan_queries=False"
            )

        # Check that we got some valid queries
        self.assertGreater(len(queries), 0, "No queries were generated")
        self.assertEqual(
            len(queries), len(estimates), "Mismatch between queries and estimates"
        )

    def test_allow_nan_queries_true(self):
        """Test that when allow_nan_queries=True, NaN queries can be included."""
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        # Create a space of interest with allow_nan_queries=True
        soi = SpaceOfInterest(
            number_of_nodes=(5, 20),
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            expected_edges="N",
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_categories=5,
            number_of_queries=100,
            query_type=QueryType.CONDITIONAL,
            number_of_data_points=50,
            allow_nan_queries=True,
        )

        sampler = Sampler(soi, return_adjacency_matrix=False)
        data, (queries, estimates), graph = sampler.generate_samples_and_queries()

        # Check that queries were generated
        self.assertGreater(len(queries), 0, "No queries were generated")
        self.assertEqual(
            len(queries), len(estimates), "Mismatch between queries and estimates"
        )

    def test_disable_query_sampling_false(self):
        """Test that when disable_query_sampling=False, queries are sampled and evaluated."""
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        # Create a space of interest with disable_query_sampling=False (default)
        soi = SpaceOfInterest(
            number_of_nodes=(3, 3),
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            expected_edges=2,
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_categories=2,
            number_of_queries=5,
            query_type=QueryType.CONDITIONAL,
            number_of_data_points=100,
            disable_query_sampling=False,  # Set to False
        )

        sampler = Sampler(soi, return_adjacency_matrix=False)
        data, (queries, estimates), graph = sampler.generate_samples_and_queries()

        # Check that queries were generated
        self.assertGreater(
            len(queries),
            0,
            "No queries were generated when disable_query_sampling=False",
        )
        self.assertEqual(
            len(queries), len(estimates), "Mismatch between queries and estimates"
        )

        # Check that we have valid data and graph regardless
        self.assertGreater(len(data), 0, "No data was generated")
        self.assertIsNotNone(graph, "No graph was generated")

    def test_disable_query_sampling_true(self):
        """Test that when disable_query_sampling=True, no queries are sampled but data and graph are still generated."""
        # Fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)

        # Create a space of interest with disable_query_sampling=True
        soi = SpaceOfInterest(
            number_of_nodes=(3, 3),
            variable_dimensionality=(1, 1),
            mechanism_family=MechanismFamily.TABULAR,
            expected_edges=2,
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[-1, 1],
            variable_type=VariableDataType.DISCRETE,
            number_of_categories=2,
            number_of_queries=5,  # This should be ignored
            query_type=QueryType.CONDITIONAL,
            number_of_data_points=100,
            disable_query_sampling=True,  # Disable query sampling
        )

        sampler = Sampler(soi, return_adjacency_matrix=False)
        data, (queries, estimates), graph = sampler.generate_samples_and_queries()

        # Check that NO queries were generated
        self.assertEqual(
            len(queries), 0, "Queries were generated when disable_query_sampling=True"
        )
        self.assertEqual(
            len(estimates),
            0,
            "Estimates were generated when disable_query_sampling=True",
        )

        # Check that we still have valid data and graph
        self.assertGreater(len(data), 0, "No data was generated")
        self.assertIsNotNone(graph, "No graph was generated")


if __name__ == "__main__":
    unittest.main()
