import unittest
from unittest.mock import MagicMock

import numpy as np

from causal_profiler.constants import (
    MechanismFamily,
    NoiseDistribution,
    NoiseMode,
    VariableDataType,
)
from causal_profiler.scm import SCM
from causal_profiler.variable import Variable


class TestSCMSampleData(unittest.TestCase):
    def setUp(self):
        # Create a simple SCM setup with mock variables and mechanisms
        self.batch_size = 10
        self.var_x = Variable(
            name="X",
            dimensionality=1,
            exogenous=False,
            variable_type=VariableDataType.CONTINUOUS,
        )
        self.var_y = Variable(
            name="Y",
            dimensionality=1,
            exogenous=False,
            variable_type=VariableDataType.CONTINUOUS,
        )

        self.scm = SCM(
            variables=[self.var_x, self.var_y],
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_mode=NoiseMode.ADDITIVE,
            noise_args=[0, 1],  # Mean=0, Std=1
            n_samples=10,
        )

        # Mock the mechanism for X and Y
        self.mock_mechanism_y = MagicMock(
            return_value=np.array([[42]] * self.batch_size)
        )  # Mocked output
        self.scm.set_function(
            variable=self.var_y,
            mechanism_family=MechanismFamily.LINEAR,
            mechanism_args=[],
        )
        self.scm.mechanisms[self.var_y.name] = self.mock_mechanism_y
        self.mock_mechanism_x = MagicMock(
            return_value=np.array([[42]] * self.batch_size)
        )  # Mocked output
        self.scm.set_function(
            variable=self.var_x,
            mechanism_family=MechanismFamily.LINEAR,
            mechanism_args=[],
        )
        self.scm.mechanisms[self.var_x.name] = self.mock_mechanism_x

    def test_sample_data_correct_shape(self):
        # Test that sample_data returns the correct number of samples
        total_samples = 50
        batch_size = self.batch_size
        data = self.scm.sample_data(total_samples=total_samples, batch_size=batch_size)

        for var_id in data:
            self.assertEqual(
                data[var_id].shape[0],
                total_samples,
                f"Incorrect sample size for variable {var_id}",
            )

    # TODO: for now batch_size has to divide the number of samples you want
    # def test_sample_data_batches(self):
    #     # Test that sample_data handles batches properly
    #     total_samples = 25
    #     batch_size = self.batch_size
    #     data = self.scm.sample_data(total_samples=total_samples, batch_size=batch_size)

    #     for var_id, values in data.items():
    #         self.assertEqual(
    #             values.shape[0], total_samples, f"Incorrect total samples for {var_id}"
    #         )

    def test_sample_data_mechanism_called(self):
        # Test that the mocked mechanism is called during sample_data
        total_samples = 20
        batch_size = self.batch_size
        self.scm.sample_data(total_samples=total_samples, batch_size=batch_size)

        self.mock_mechanism_y.assert_called()

    def test_sample_data_noise_sampling(self):
        # Test that noise is being generated
        total_samples = 10
        data = self.scm.sample_data(total_samples=total_samples)
        noise_var = f"U_{self.var_x.name}"

        self.assertIn(noise_var, data, "Noise variable not found in sampled data")
        self.assertEqual(
            data[noise_var].shape[0], total_samples, "Incorrect noise sampling shape"
        )

    def test_sample_data_invalid_batch_size(self):
        # Test behavior with invalid batch sizes
        total_samples = 10
        batch_size = 0  # Invalid batch size

        with self.assertRaises(ValueError):
            self.scm.sample_data(total_samples=total_samples, batch_size=batch_size)


if __name__ == "__main__":
    unittest.main()
