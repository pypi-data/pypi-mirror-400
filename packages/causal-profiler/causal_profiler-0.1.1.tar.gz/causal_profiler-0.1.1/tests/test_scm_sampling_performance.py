import multiprocessing as mp
import random
import time
import unittest
from collections import defaultdict, deque
from functools import partial

import numpy as np

from causal_profiler.constants import (
    MechanismFamily,
    NoiseDistribution,
    NoiseMode,
    VariableDataType,
)
from causal_profiler.scm import SCM
from causal_profiler.variable import Variable

VAR_DIMENSIONALITY = 10
NUM_VARIABLES_PER_SCM = 20


def introduces_cycle(graph, start, end):
    visited = set()
    stack = deque([start])

    while stack:
        node = stack.pop()
        if node == end:  # A cycle is formed
            return True
        if node not in visited:
            visited.add(node)
            stack.extend(graph[node])
    return False


def generate_random_scm(num_variables: int) -> SCM:
    variables = []
    for i in range(num_variables):
        var = Variable(
            name=f"X{i}",
            dimensionality=VAR_DIMENSIONALITY,
            exogenous=False,
            variable_type=VariableDataType.CONTINUOUS,
        )
        variables.append(var)

    scm = SCM(
        variables=variables,
        noise_distribution=NoiseDistribution.GAUSSIAN,
        noise_mode=NoiseMode.ADDITIVE,
        noise_args=[0, 1],  # mean=0, std=1
    )

    # Adjacency list representation of the graph
    graph = defaultdict(list)
    # Randomly add edges
    for from_var in variables:
        for to_var in variables:
            if not introduces_cycle(graph, to_var.name, from_var.name):
                if (
                    from_var != to_var and random.random() < 0.3
                ):  # 30% chance to add an edge
                    scm.add_edge(from_var, to_var)
                    graph[from_var.name].append(to_var.name)

    # Set mechanisms for variables
    for var in variables:
        scm.set_function(variable=var, mechanism_family=MechanismFamily.LINEAR)

    return scm


# Function to generate N SCMs and sample M data points from each
def sample_from_scm(scm_index, num_variables_per_scm, n_samples):
    np.random.seed(scm_index)
    random.seed(scm_index)
    scm = generate_random_scm(num_variables_per_scm)
    scm.n_samples = n_samples
    scm.reset_values()
    scm.sample_noise_variables()
    scm.compute_variables()
    # Collect data (not storing to save memory)
    return scm_index  # Return index as a placeholder


def sample_from_scm_new(scm_index, num_variables_per_scm, n_samples):
    np.random.seed(scm_index)
    random.seed(scm_index)
    scm = generate_random_scm(num_variables_per_scm)
    data = scm.sample_data(total_samples=n_samples, batch_size=n_samples)
    return scm_index, data


class TestSCMSamplingPerformance(unittest.TestCase):

    def setUp(self):
        # Define the range of N (number of SCMs) and M (number of samples per SCM) to test
        self.test_cases = [
            {"N": 10, "M": 1000},
            {"N": 10, "M": 10000},
            {"N": 10, "M": 100000},
            {"N": 50, "M": 1000},
            {"N": 50, "M": 10000},
            {"N": 50, "M": 100000},
            {"N": 100, "M": 1000},
            {"N": 100, "M": 10000},
            {"N": 100, "M": 100000},
        ]
        self.num_variables_per_scm = NUM_VARIABLES_PER_SCM

    def generate_and_sample_scms(self, N, M):
        partial_sample_from_scm = partial(
            # sample_from_scm,
            sample_from_scm_new,
            num_variables_per_scm=self.num_variables_per_scm,
            n_samples=M,
        )
        with mp.Pool(processes=mp.cpu_count()) as pool:
            results = pool.map(partial_sample_from_scm, range(N))

    def test_scm_sampling_performance(self):
        for case in self.test_cases:
            N = case["N"]
            M = case["M"]
            print(
                f"\nBenchmarking with N={N} SCMs, M={M} samples per SCM, VarsPerSCM: {NUM_VARIABLES_PER_SCM}, dimensionality: {VAR_DIMENSIONALITY}"
            )
            start_time = time.perf_counter()
            self.generate_and_sample_scms(N, M)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            avg_time_per_scm = total_time / N
            avg_time_per_sample = total_time / (N * M)
            print(f"Total time: {total_time:.2f} seconds")
            print(f"Average time per SCM: {avg_time_per_scm:.2f} seconds")
            print(
                f"Average time per sample: {avg_time_per_sample*1000:.6f} milliseconds"
            )


if __name__ == "__main__":
    unittest.main()
