import random
import unittest

import numpy as np
import torch

from causal_profiler.constants import (
    MechanismFamily,
    NeuralNetworkType,
    NoiseDistribution,
    NoiseMode,
)
from causal_profiler.scm import SCM, Variable


def create_multidimensional_scm():
    """
    Create an SCM with multi-dimensional inputs and outputs for testing.
    """
    # Create variables with dimensionality > 1
    X = Variable(name="X", dimensionality=2, exogenous=True)
    Y = Variable(name="Y", dimensionality=2)
    Z = Variable(name="Z", dimensionality=4)

    # Initialize SCM
    scm = SCM(
        variables=[X, Y, Z],
        noise_distribution=NoiseDistribution.GAUSSIAN,
        noise_mode=NoiseMode.ADDITIVE,
        noise_args=[0, 1],  # mean=0, std=1
    )

    # Add edges
    scm.add_edge(X, Y)
    scm.add_edge(Y, Z)

    # Set mechanisms
    scm.set_function(
        variable=Y,
        mechanism_family=MechanismFamily.NEURAL_NETWORK,
        mechanism_args=[NeuralNetworkType.FEEDFORWARD, 3],
    )
    scm.set_function(
        variable=Z,
        mechanism_family=MechanismFamily.NEURAL_NETWORK,
        mechanism_args=[NeuralNetworkType.FEEDFORWARD, 3],
    )

    return scm


class TestSCMMultiDimensional(unittest.TestCase):
    def test_noise_sampling(self):
        scm = create_multidimensional_scm()
        scm.n_samples = 100  # Batch size

        scm.sample_noise_variables()

        # Check that noise variables have the correct shape
        X = scm.variables["X"]
        self.assertEqual(X.value.shape, (100, 2))  # 100 samples, 2 dimensions

        U_Z = scm.variables["U_Z"]
        self.assertEqual(U_Z.value.shape, (100, 4))  # 100 samples, 4 dimensions

    def test_variable_computation(self):
        scm = create_multidimensional_scm()
        scm.n_samples = 50  # Batch size

        # Sample noise and compute all variables
        scm.reset_values()
        scm.sample_noise_variables()
        scm.compute_variables()

        # Check that variables have the correct shapes
        X = scm.variables["X"]
        Y = scm.variables["Y"]
        Z = scm.variables["Z"]

        self.assertEqual(X.value.shape, (50, 2))  # X: 2 dimensions
        self.assertEqual(Y.value.shape, (50, 2))  # Y: 2 dimensions
        self.assertEqual(Z.value.shape, (50, 4))  # Z: 4 dimensions

    def test_dependency_propagation(self):
        scm = create_multidimensional_scm()
        scm.n_samples = 10  # Batch size

        # Reset and sample variables
        scm.reset_values()
        scm.sample_noise_variables()

        # Manually compute Y and Z
        scm.compute_variable(scm.variables["Y"])
        scm.compute_variable(scm.variables["Z"])

        # Ensure all parents of Z (Y) have non-None values
        for parent_id in scm.parents["Z"]:
            parent_var = scm.variables[parent_id]
            self.assertIsNotNone(parent_var.value)

        # Ensure Z's value is computed
        Z = scm.variables["Z"]
        self.assertIsNotNone(Z.value)
        self.assertEqual(Z.value.shape, (10, 4))  # 10 samples, 4 dimensions

    def test_end_to_end_sampling_and_computation(self):
        scm = create_multidimensional_scm()
        scm.n_samples = 20  # Batch size

        # Reset, sample, and compute
        scm.reset_values()
        scm.sample_noise_variables()
        scm.compute_variables()

        # Check final computed values for all variables
        data = {var_id: var.value for var_id, var in scm.variables.items()}
        for var_id, values in data.items():
            self.assertIsNotNone(values)  # Ensure values are computed
            self.assertEqual(values.shape[0], 20)  # Check batch size consistency

    def seed_everything(self, seed):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    def test_consistency_with_seed(self):
        self.seed_everything(42)  # for reproducibility
        scm1 = create_multidimensional_scm()
        scm1.n_samples = 30

        scm1.reset_values()
        scm1.sample_noise_variables()
        scm1.compute_variables()

        self.seed_everything(42)  # Reset seed
        scm2 = create_multidimensional_scm()
        scm2.n_samples = 30

        scm2.reset_values()
        scm2.sample_noise_variables()
        scm2.compute_variables()

        # Ensure all variables are consistent between runs
        for var_id in scm1.variables.keys():
            np.testing.assert_array_almost_equal(
                scm1.variables[var_id].value, scm2.variables[var_id].value
            )
