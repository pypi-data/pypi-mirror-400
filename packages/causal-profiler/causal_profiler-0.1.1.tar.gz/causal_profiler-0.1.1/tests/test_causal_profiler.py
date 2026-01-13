import random
import unittest
from itertools import chain

import numpy as np

from causal_profiler.constants import (
    ErrorMetric,
    FunctionSampling,
    MechanismFamily,
    NoiseDistribution,
    QueryType,
    VariableDataType,
)
from causal_profiler.query import Query
from causal_profiler.space_of_interest import SpaceOfInterest
from causal_profiler import CausalProfiler


class TestCausalProfiler(unittest.TestCase):

    def test_sampler(self):
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
            number_of_noise_regions="N",
            variable_type=VariableDataType.DISCRETE,
            number_of_queries=2,
            query_type=QueryType.CONDITIONAL,
            number_of_data_points=100,
        )

        profiler = CausalProfiler(soi, return_adjacency_matrix=False)
        data, (queries, estimates), (graph, index_to_variable) = (
            profiler.generate_samples_and_queries()
        )

        # Check data shape
        self.assertEqual(len(data), 5)  # 5 variables
        for var_id, values in data.items():
            self.assertEqual(values.shape[0], 100)

        # Check queries
        self.assertEqual(len(queries), 2)
        self.assertEqual(len(estimates), 2)
        for q, e in zip(queries, estimates):
            self.assertTrue(isinstance(q, Query))
            self.assertTrue(isinstance(e, float) or isinstance(e, np.number))

        # Check graph
        self.assertIsInstance(graph, dict)
        # Keys should match variable IDs
        self.assertEqual(set(index_to_variable), set(data.keys()))

    def test_evaluate_error(self):
        profiler = CausalProfiler(
            SpaceOfInterest(), metric=ErrorMetric.L1, return_adjacency_matrix=False
        )

        predicted = [1.0, 3.0]
        actual = [2.0, 2.0]

        # L1 error: mean(|pred - actual|) = mean(|[1-2, 3-2]|) = mean([1,1])=1
        profiler.set_metric(ErrorMetric.L1)
        error, failures = profiler.evaluate_error(estimated=predicted, target=actual)
        self.assertAlmostEqual(error, 1.0)
        self.assertEqual(failures, 0)

        # L2 error: sqrt(mean((pred-actual)^2)) = sqrt(( (1-2)^2+(3-2)^2 )/2) = sqrt((1+1)/2)=sqrt(1)=1
        profiler.set_metric(ErrorMetric.L2)
        error, failures = profiler.evaluate_error(estimated=predicted, target=actual)
        self.assertAlmostEqual(error, 1.0)
        self.assertEqual(failures, 0)

        # MSE: mean((pred-actual)^2) = (1+1)/2=1
        profiler.set_metric(ErrorMetric.MSE)
        error, failures = profiler.evaluate_error(estimated=predicted, target=actual)
        self.assertAlmostEqual(error, 1.0)
        self.assertEqual(failures, 0)

        # MAPE: mean(|(pred-actual)/actual|)*100 = ((|1-2|/2) + (|3-2|/2))/2 *100
        # = ((1/2)+(1/2))/2 *100 = (0.5+0.5)/2 *100= (1.0/2)*100=50
        profiler.set_metric(ErrorMetric.MAPE)
        error, failures = profiler.evaluate_error(estimated=predicted, target=actual)
        self.assertAlmostEqual(error, 50.0)
        self.assertEqual(failures, 0)

        # Hamming: fraction of positions that differ
        # predicted=[1.0,3.0], actual=[2.0,2.0], both differ, so hamming = 2/2=1
        profiler.set_metric(ErrorMetric.HAMMING)
        error, failures = profiler.evaluate_error(estimated=predicted, target=actual)
        self.assertAlmostEqual(error, 1.0)
        self.assertEqual(failures, 0)

        # Cosine distance:
        # pred=[1,3], actual=[2,2]
        # dot=1*2+3*2=2+6=8
        # norm(pred)=sqrt(1+9)=sqrt(10), norm(actual)=sqrt(4+4)=sqrt(8)
        # cos_sim=8/(sqrt(10)*sqrt(8)) = 8/(sqrt(80))=8/(8.944...)~0.8944
        # cos_distance=1-0.8944=0.1056 approx
        profiler.set_metric(ErrorMetric.COSINE)
        error, failures = profiler.evaluate_error(predicted, actual)
        self.assertAlmostEqual(error, 0.1056, places=4)
        self.assertEqual(failures, 0)

        # Also test when predicted also includes queries
        predicted_values = [
            (Query(QueryType.CONDITIONAL, {}), 1.0),
            (Query(QueryType.CONDITIONAL, {}), 3.0),
        ]
        profiler.set_metric(ErrorMetric.L1)
        error, failures = profiler.evaluate_error(
            estimated=predicted_values, target=actual
        )
        self.assertAlmostEqual(error, 1.0)
        self.assertEqual(failures, 0)

    def test_evaluate_error_nan(self):
        profiler = CausalProfiler(
            SpaceOfInterest(), metric=ErrorMetric.L1, return_adjacency_matrix=False
        )

        predicted = [1.0, float("nan"), 3.0]
        actual = [2.0, 2.0, 2.0]
        profiler.set_metric(ErrorMetric.L1)
        error, failures = profiler.evaluate_error(estimated=predicted, target=actual)
        # Non-NaN are at indices 0 and 2: error=mean(|[1-2,3-2]|)=1.0, failures=1
        self.assertAlmostEqual(error, 1.0)
        self.assertEqual(failures, 1)

        # If all are NaN
        predicted = [float("nan"), float("nan")]
        actual = [1.0, 1.0]
        error, failures = profiler.evaluate_error(estimated=predicted, target=actual)
        # error=0.0, failures=2
        self.assertEqual(error, 0.0)
        self.assertEqual(failures, 2)

    def test_query_higher_variable_dimensionality(self):
        random.seed(43)
        np.random.seed(43)

        soi = SpaceOfInterest(
            number_of_nodes=(3, 3),
            variable_dimensionality=(3, 3),
            mechanism_family=MechanismFamily.TABULAR,
            expected_edges=1,
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[-1, 1],
            number_of_noise_regions="N",
            number_of_categories=2,
            variable_type=VariableDataType.DISCRETE,
            number_of_queries=10,
            query_type=QueryType.CONDITIONAL,
            number_of_data_points=50,
        )

        profiler = CausalProfiler(soi, return_adjacency_matrix=False, n_samples=1000)
        # TODO: only random sampling can currently handle dimensionality higher than 1
        profiler.sampler.function_sampling = FunctionSampling.RANDOM
        profiler.generate_samples_and_queries()
        # If this doesn't crash, then it can handle it!

    def test_query_uniqueness(self):

        for query_type in [
            QueryType.CONDITIONAL,
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
                expected_edges=1,
                noise_distribution=NoiseDistribution.UNIFORM,
                noise_args=[-1, 1],
                number_of_noise_regions="N",
                number_of_categories=2,
                variable_type=VariableDataType.DISCRETE,
                discrete_function_sampling=FunctionSampling.RANDOM,
                number_of_queries=500,  # To get duplicates, this is more than the possible ones.
                query_type=query_type,
                number_of_data_points=5,
            )

            profiler = CausalProfiler(
                soi, return_adjacency_matrix=False, n_samples=1000
            )
            data, (queries, estimates), graph = profiler.generate_samples_and_queries()

            # Ensure uniqueness
            q_strs = set(str(q) for q in queries)
            self.assertEqual(len(q_strs), len(queries))

    def test_queries_support_multiple_variables(self):
        for query_type in [
            QueryType.CONDITIONAL,
            QueryType.CATE,
            QueryType.CTF_TE,
        ]:
            random.seed(43)
            np.random.seed(43)

            soi = SpaceOfInterest(
                number_of_nodes=(4, 4),
                variable_dimensionality=(1, 1),
                mechanism_family=MechanismFamily.TABULAR,
                expected_edges=1,
                noise_distribution=NoiseDistribution.UNIFORM,
                noise_args=[-1, 1],
                number_of_noise_regions="N",
                number_of_categories=2,
                variable_type=VariableDataType.DISCRETE,
                number_of_queries=100,
                query_type=query_type,
                number_of_data_points=5,
            )

            profiler = CausalProfiler(
                soi, return_adjacency_matrix=False, n_samples=1000
            )
            data, (queries, estimates), graph = profiler.generate_samples_and_queries()

            # Check that at least one query has more than one conditioned variable
            for query in queries:
                _, conditioning_vars = query.get_conditioned_info()
                if len(conditioning_vars) > 1:
                    break
            else:
                self.fail(
                    "No query has more than one variable in the conditioning variables."
                )

    def test_query_variables_have_no_values(self):
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
            number_of_categories=3,
            variable_type=VariableDataType.DISCRETE,
            number_of_queries=100,
            query_type=QueryType.CTF_TE,
            number_of_data_points=50,
        )

        profiler = CausalProfiler(soi, return_adjacency_matrix=False)
        data, (queries, estimates), graph = profiler.generate_samples_and_queries()

        for query in queries:
            for var in chain.from_iterable(query.vars.values()):
                assert var.value is None

    def test_discrete_function_sampling_from_space_of_interest(self):
        # Test that discrete_function_sampling from SpaceOfInterest is correctly passed to Sampler
        for function_sampling in FunctionSampling:
            # Create SpaceOfInterest with specific discrete_function_sampling
            soi = SpaceOfInterest(
                discrete_function_sampling=function_sampling,
                variable_type=VariableDataType.DISCRETE,
            )

            # Create CausalProfiler
            profiler = CausalProfiler(soi)

            # Verify the function_sampling is passed to the Sampler
            self.assertEqual(profiler.sampler.function_sampling, function_sampling)


if __name__ == "__main__":
    unittest.main()
