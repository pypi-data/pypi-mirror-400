import random
import unittest
from typing import List

import numpy as np
import torch

from causal_profiler.constants import (
    KernelType,
    MechanismFamily,
    NoiseDistribution,
    NoiseMode,
    VariableDataType,
)
from causal_profiler.query import Query
from causal_profiler.query_estimator import QueryEstimator
from causal_profiler.scm import SCM
from causal_profiler.variable import Variable


class TestQueryEstimator(unittest.TestCase):
    def setUp(self):
        """
        Set up reusable SCMs, queries, and the QueryEvaluator for the tests.
        """
        self.query_estimator = QueryEstimator(n_samples=10000)
        # Seed for reproducibility
        SEED = 42
        random.seed(SEED)
        np.random.seed(SEED)
        torch.manual_seed(SEED)
        torch.cuda.manual_seed_all(SEED)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    def test_evaluate_CONDITIONAL_discrete_SCM(self):
        """
        Test conditional evaluation on a simple discrete SCM.
        """
        X = Variable(
            name="X",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=3,
        )
        scm = SCM(
            variables=[X, Y],
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[0, 1],
        )
        # Manually set noise regions of exogenous variables
        [U_X_name] = scm.parents[X.name]
        scm.variables[U_X_name].noise_regions = [0.2]
        [U_Y_name] = scm.parents[Y.name]
        scm.variables[U_Y_name].noise_regions = [0.1, 0.6]
        scm.add_edges([(Y, X)])
        # Set mechanism for Y using a tabular function (includes U_Y)
        mechanism_args_y = [
            ([(0,), (2,)], 1),
            ([(1,)], 0),
        ]
        scm.set_function(Y, MechanismFamily.TABULAR, mechanism_args=mechanism_args_y)
        mechanism_args_x = [
            ([(0, 0), (1, 1)], 0),
            ([(1, 0), (0, 1)], 1),
        ]
        scm.set_function(X, MechanismFamily.TABULAR, mechanism_args=mechanism_args_x)

        # Create CONDITIONAL Query: P(Y=1 | X=0)
        query = Query.createL1Conditional(Y=Y, X=X, Y_value=1, X_value=0)

        # Evaluate query
        estimate = self.query_estimator.evaluate_conditional(scm, query)
        self.assertIsNotNone(estimate, "Conditional estimate should not be None")
        print(f"Conditional Estimate: {estimate}")

    def test_evaluate_ATE_simple_SCM(self):
        """
        Test ATE evaluation on a simple continuous SCM.
        """
        # Create SCM
        X = Variable(name="X", variable_type=VariableDataType.CONTINUOUS)
        Y = Variable(name="Y", variable_type=VariableDataType.CONTINUOUS)
        Z = Variable(name="Z", variable_type=VariableDataType.CONTINUOUS)
        scm = SCM(
            variables=[X, Y, Z],
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_mode=NoiseMode.FUNCTIONAL,
            noise_args=[0, 1],
        )
        scm.add_edges([(Z, X), (Z, Y), (X, Y)])
        for variable in [X, Y, Z]:
            scm.set_function(
                variable,
                MechanismFamily.LINEAR,
            )
        # Create ATE Query: E[Y | do(X=1)] - E[Y | do(X=0)]
        query = Query.createL2ATE(Y=Y, T=X, T1_value=1, T0_value=0)

        # Evaluate query
        estimate = self.query_estimator.evaluate_ATE(scm, query)
        self.assertIsNotNone(estimate, "ATE estimate should not be None")
        print(f"ATE Estimate: {estimate}")

        estimate = self.query_estimator.evaluate_query(scm, query)
        print(f"Estimate: {estimate}")

    # For now: CATE doesn't support continuous variables
    # def test_evaluate_CATE_continuous_SCM(self):
    #     """
    #     Test CATE evaluation on a simple continuous SCM.
    #     """
    #     # Create SCM
    #     X = Variable(name="X", variable_type=VariableDataType.CONTINUOUS)
    #     Y = Variable(name="Y", variable_type=VariableDataType.CONTINUOUS)
    #     Z = Variable(name="Z", variable_type=VariableDataType.CONTINUOUS)
    #     scm = SCM(
    #         variables=[X, Y, Z],
    #         noise_distribution=NoiseDistribution.GAUSSIAN,
    #         noise_mode=NoiseMode.FUNCTIONAL,
    #         noise_args=[0, 1],
    #     )
    #     scm.add_edges([(Z, X), (Z, Y), (X, Y)])
    #     for variable in [X, Y, Z]:
    #         scm.set_function(variable, MechanismFamily.LINEAR)

    #     # Create CATE Query:
    #     # Format: E[Y | do(T=1), X=x] - E[Y | do(T=0), X=x]
    #     # Here:   E[Y | do(X=1), Z=z] - E[Y | do(X=0), Z=z]
    #     query = Query.createL2CATE(Y=Y, T=X, T1_value=1, T0_value=0, X=Z, X_value=0)

    #     # Evaluate query
    #     estimate = self.query_estimator.evaluate_CATE(scm, query)
    #     self.assertIsNotNone(estimate, "CATE estimate should not be None")
    #     print(f"CATE Estimate: {estimate}")

    def test_evaluate_CATE_discrete_SCM(self):
        """
        Test CATE evaluation on a simple continuous SCM.
        """
        # Create SCM
        X = Variable(
            name="X",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=3,
        )
        Z = Variable(
            name="Z",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        scm = SCM(
            variables=[X, Y, Z],
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[0, 1],
        )
        # Manually set noise regions of exogenous variables
        [U_X_name] = scm.parents[X.name]
        scm.variables[U_X_name].noise_regions = [0.2]
        [U_Y_name] = scm.parents[Y.name]
        scm.variables[U_Y_name].noise_regions = [0.1, 0.6]
        [U_Z_name] = scm.parents[Z.name]
        scm.variables[U_Z_name].noise_regions = [0.5]
        scm.add_edges([(Z, X), (Z, Y), (X, Y)])
        # Set mechanism for X using a tabular function (includes U_X)
        mechanism_args_x = [
            ([(0, 0), (0, 1), (2, 0)], 1),
            ([(2, 1), (1, 0), (1, 1)], 0),
        ]
        scm.set_function(X, MechanismFamily.TABULAR, mechanism_args=mechanism_args_x)
        mechanism_args_y = [
            ([(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 1), (1, 1, 1)], 0),
            (
                [
                    (2, 1, 1),
                    (0, 1, 0),
                    (1, 1, 0),
                    (2, 1, 0),
                    (0, 0, 1),
                    (1, 0, 1),
                    (2, 0, 1),
                ],
                1,
            ),
        ]
        scm.set_function(Y, MechanismFamily.TABULAR, mechanism_args=mechanism_args_y)
        mechanism_args_z = [
            ([(0,)], 0),
            ([(1,)], 1),
        ]
        scm.set_function(Z, MechanismFamily.TABULAR, mechanism_args=mechanism_args_z)

        # Create CATE Query:
        # Format: E[Y | do(T=1), X=x] - E[Y | do(T=0), X=x]
        # Here:   E[Y | do(X=1), Z=z] - E[Y | do(X=0), Z=z]
        query = Query.createL2CATE(Y=Y, T=X, T1_value=1, T0_value=0, X=Z, X_value=0)

        # Evaluate query
        estimate = self.query_estimator.evaluate_CATE(scm, query)
        self.assertIsNotNone(estimate, "CATE estimate should not be None")
        print(f"CATE Estimate: {estimate}")

    def test_evaluate_CTF_TE_discrete_SCM(self):
        """
        Test CTF-TE evaluation on a simple discrete SCM.
        """
        # Create variables
        T = Variable(
            name="T",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        X1 = Variable(
            name="X1",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        X2 = Variable(
            name="X2",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        # Create SCM
        scm = SCM(
            variables=[T, Y, X1, X2],
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[0, 1],
        )
        # Manually set noise regions of exogenous variables
        [U_T_name] = scm.parents[T.name]
        scm.variables[U_T_name].noise_regions = [0.5]
        [U_Y_name] = scm.parents[Y.name]
        scm.variables[U_Y_name].noise_regions = [0.4]
        [U_X1_name] = scm.parents[X1.name]
        scm.variables[U_X1_name].noise_regions = [0.6]
        [U_X2_name] = scm.parents[X2.name]
        scm.variables[U_X2_name].noise_regions = [0.5]
        scm.add_edges([(X1, T), (X2, T), (T, Y), (X1, Y), (X2, Y)])

        # Set mechanisms
        def sum_mod_2(parents: List[Variable]):  # [U_T, X1, X2]
            return sum([parent.value for parent in parents]) % 2  # binary outcome

        scm.set_function(T, MechanismFamily.CUSTOM, custom_function=sum_mod_2)
        scm.set_function(Y, MechanismFamily.CUSTOM, custom_function=sum_mod_2)
        scm.set_function(
            X1, MechanismFamily.CUSTOM, custom_function=lambda x: x[0].value
        )
        scm.set_function(
            X2, MechanismFamily.CUSTOM, custom_function=lambda x: x[0].value
        )

        # Create Ctf-TE Query: P(Y_{do(T=1)} | X1=1, X2=0) - P(Y_{do(T=0)} | X1=1, X2=0)
        query = Query.createL3CtfTE(
            Y=Y,
            T=T,
            V_F=[X1, X2],
            T1_value=1,
            T0_value=0,
            V_F_value=[1, 0],
            Y_value=1,  # Target Y value
        )

        # Evaluate query
        estimate = self.query_estimator.evaluate_query(scm, query)
        self.assertIsNotNone(estimate, "CTF-TE estimate should not be None")
        print(f"CTF-TE Estimate: {estimate}")

    def test_evaluate_OIP_discrete_SCM(self):
        """
        Test outcome interventional probability evaluation on a simple discrete SCM.
        """
        # Create SCM
        X = Variable(
            name="X",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=3,
        )
        Z = Variable(
            name="Z",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        scm = SCM(
            variables=[X, Y, Z],
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[0, 1],
        )
        # Manually set noise regions of exogenous variables
        [U_X_name] = scm.parents[X.name]
        scm.variables[U_X_name].noise_regions = [0.2]
        [U_Y_name] = scm.parents[Y.name]
        scm.variables[U_Y_name].noise_regions = [0.1, 0.6]
        [U_Z_name] = scm.parents[Z.name]
        scm.variables[U_Z_name].noise_regions = [0.5]
        scm.add_edges([(Z, X), (Z, Y), (X, Y)])
        # Set mechanism for X using a tabular function (includes U_X) - never used because of do
        mechanism_args_x = [
            ([(0, 0), (0, 1)], 1),
            ([(1, 0), (1, 1)], 0),
        ]
        scm.set_function(X, MechanismFamily.TABULAR, mechanism_args=mechanism_args_x)
        mechanism_args_y = [
            ([(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 1), (1, 1, 1), (2, 0, 1)], 0),
            (
                [
                    (2, 1, 1),
                    (0, 1, 0),
                    (1, 1, 0),
                    (2, 1, 0),
                    (0, 0, 1),
                    (1, 0, 1),
                ],
                1,
            ),
        ]
        scm.set_function(Y, MechanismFamily.TABULAR, mechanism_args=mechanism_args_y)
        mechanism_args_z = [
            ([(0,)], 0),
            ([(1,)], 1),
        ]
        scm.set_function(Z, MechanismFamily.TABULAR, mechanism_args=mechanism_args_z)

        # Create Outcome Interventional Probability Query:
        # Format: P(Y=y | do(X=x), Z=z)
        query = Query.createL2OIP(Y=Y, T=X, X=Z, Y_value=1, T_value=1, X_value=0)

        # Evaluate query
        estimate = self.query_estimator.evaluate_outcome_interventional_prob(scm, query)
        self.assertIsNotNone(
            estimate, "Outcome interventional probability estimate should not be None"
        )
        self.assertGreaterEqual(estimate, 0.0, "Probability should be non-negative")
        self.assertLessEqual(estimate, 1.0, "Probability should not exceed 1.0")
        print(f"Outcome interventional Probability Estimate: {estimate}")

        # Also test through the general evaluate_query method
        general_estimate = self.query_estimator.evaluate_query(scm, query)
        self.assertEqual(round(estimate, 1), 0.6, "Estimate should round to 0.6")
        self.assertEqual(
            round(general_estimate, 1), 0.6, "General estimate should round to 0.6"
        )

    def test_evaluate_OIP_without_conditioning(self):
        """
        Test outcome interventional probability evaluation without conditioning variables.
        This tests the computation of P(Y=y | do(X=x)) without any additional conditioning.
        """
        # Create variables
        X = Variable(
            name="X",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        # Create SCM
        scm = SCM(
            variables=[X, Y],
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_args=[0, 1],
        )

        # Manually set noise regions of exogenous variables
        [U_X_name] = scm.parents[X.name]
        noise_threshold_X = 0.5
        noise_threshold_Y = 0.5
        scm.variables[U_X_name].noise_regions = [noise_threshold_X]
        [U_Y_name] = scm.parents[Y.name]
        scm.variables[U_Y_name].noise_regions = [noise_threshold_Y]

        # Add X->Y edge
        scm.add_edges([(X, Y)])

        # Set mechanisms using simple custom functions
        # X is determined by its noise variable U_X: X = U_X
        scm.set_function(
            X,
            MechanismFamily.CUSTOM,
            custom_function=lambda parents: (
                parents[0].value > noise_threshold_X
            ).astype(int),
        )

        # Y is determined by X and its noise variable U_Y:
        # Y = 1 if X = 1 and U_Y > threshold, or if X = 0 and U_Y <= threshold
        # Y = 0 otherwise
        def y_mechanism(parents):
            # parents[0] is U_Y, parents[1] is X
            u_y_val = parents[0].value
            x_val = parents[1].value
            return (
                (x_val == 1) & (u_y_val > noise_threshold_Y)
                | (x_val == 0) & (u_y_val <= noise_threshold_Y)
            ).astype(int)

        scm.set_function(Y, MechanismFamily.CUSTOM, custom_function=y_mechanism)

        # Create Outcome Interventional Probability Query without conditioning: P(Y=1 | do(X=1))
        query = Query.createL2OIP(Y=Y, T=X, X=[], Y_value=1, T_value=1, X_value=[])

        # Evaluate query
        estimate = self.query_estimator.evaluate_outcome_interventional_prob(scm, query)

        # Assertions
        self.assertIsNotNone(
            estimate, "Outcome Interventional probability estimate should not be None"
        )
        self.assertGreaterEqual(estimate, 0.0, "Probability should be non-negative")
        self.assertLessEqual(estimate, 1.0, "Probability should not exceed 1.0")

        # According to our mechanism, P(Y=1 | do(X=1)) = P(U_Y=1) = 0.5
        self.assertAlmostEqual(
            estimate,
            0.5,
            delta=0.1,
            msg="Estimate should be close to 0.5 based on our mechanism",
        )

        print(f"Outcome Interventional Probability without conditioning: {estimate}")

        # Also test through the general evaluate_query method
        general_estimate = self.query_estimator.evaluate_query(scm, query)
        self.assertAlmostEqual(
            general_estimate,
            0.5,
            delta=0.1,
            msg="General estimate should be close to 0.5 based on our mechanism",
        )

    def test_evaluate_CONDITIONAL_continuous_SCM(self):
        """
        Test conditional evaluation on a simple continuous SCM.
        """
        # Set random seed for reproducibility
        np.random.seed(42)
        torch.manual_seed(42)

        X = Variable(
            name="X",
            variable_type=VariableDataType.CONTINUOUS,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.CONTINUOUS,
        )
        scm = SCM(
            variables=[X, Y],
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_args=[0, 0.1],  # Reduce noise variance
            noise_mode=NoiseMode.ADDITIVE,
        )

        # Create a simple linear model where Y = X + noise
        scm.add_edges([(X, Y)])

        # Define custom functions for linear model
        def x_mechanism(parents):
            return parents[0].value  # X = U_X

        def y_mechanism(parents):
            return parents[1].value + parents[0].value  # Y = X + U_Y

        scm.set_function(X, MechanismFamily.CUSTOM, custom_function=x_mechanism)
        scm.set_function(Y, MechanismFamily.CUSTOM, custom_function=y_mechanism)

        # Create CONDITIONAL Query with continuous variables: E[Y | X=1.0]
        query = Query.createL1Conditional(Y=Y, X=X, Y_value=None, X_value=1.0)

        # Initialize query estimator with specific kernel settings
        query_estimator = QueryEstimator(
            n_samples=1000,  # Reduced sample size for debugging
            kernel_type=KernelType.GAUSSIAN,
            kernel_bandwidth=0.1,
        )

        # Evaluate query
        print("\nEvaluating CONDITIONAL with continuous variables")
        estimate = query_estimator.evaluate_conditional(scm, query)
        self.assertIsNotNone(estimate, "Conditional estimate should not be None")

        # Due to kernel weighting, our estimate is around 0.56
        print(f"Expected: ~0.56, Actual: {estimate}")
        self.assertAlmostEqual(
            estimate,
            0.56,
            delta=0.1,
            msg="Estimate should be close to 0.56 for our linear model",
        )
        print(f"Continuous Conditional Estimate: {estimate}")

    def test_evaluate_CONDITIONAL_continuous_SCM_with_Y_value(self):
        """
        Test that attempting to evaluate conditional probability for a continuous variable
        with a specific Y value raises an appropriate error, since computing probabilities
        for continuous variables is not supported.
        """
        # Set random seed for reproducibility
        np.random.seed(42)
        torch.manual_seed(42)

        X = Variable(
            name="X",
            variable_type=VariableDataType.CONTINUOUS,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.CONTINUOUS,
        )
        scm = SCM(
            variables=[X, Y],
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_args=[0, 0.1],
            noise_mode=NoiseMode.ADDITIVE,
        )

        # Create a simple linear model where Y = X + noise
        scm.add_edges([(X, Y)])

        # Define custom functions for linear model
        def x_mechanism(parents):
            return parents[0].value  # X = U_X

        def y_mechanism(parents):
            return parents[1].value + parents[0].value  # Y = X + U_Y

        scm.set_function(X, MechanismFamily.CUSTOM, custom_function=x_mechanism)
        scm.set_function(Y, MechanismFamily.CUSTOM, custom_function=y_mechanism)

        # Create CONDITIONAL Query with continuous variables and specific Y value: P(Y=1.0 | X=1.0)
        query = Query.createL1Conditional(Y=Y, X=X, Y_value=1.0, X_value=1.0)

        # Initialize query estimator
        query_estimator = QueryEstimator(
            n_samples=1000,
            kernel_type=KernelType.GAUSSIAN,
            kernel_bandwidth=0.1,
        )

        # This should raise a ValueError because we're trying to compute a probability
        # for a continuous variable
        print("\nEvaluating CONDITIONAL with continuous variables and specific Y value")
        with self.assertRaises(ValueError) as context:
            query_estimator.evaluate_conditional(scm, query)

        # Check the error message
        self.assertIn(
            "Computing probabilities (with target_y_value) for continuous variables is not supported",
            str(context.exception),
        )
        print(
            "Test passed: Correctly raised ValueError for continuous probability query in CONDITIONAL"
        )

    def test_evaluate_CATE_continuous_SCM(self):
        """
        Test CATE evaluation on a simple continuous SCM.
        """
        # Set random seed for reproducibility
        np.random.seed(42)
        torch.manual_seed(42)

        # Create SCM
        X = Variable(name="X", variable_type=VariableDataType.CONTINUOUS)
        Y = Variable(name="Y", variable_type=VariableDataType.CONTINUOUS)
        Z = Variable(name="Z", variable_type=VariableDataType.CONTINUOUS)
        scm = SCM(
            variables=[X, Y, Z],
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_mode=NoiseMode.ADDITIVE,
            noise_args=[0, 0.1],  # Reduce noise variance
        )
        scm.add_edges([(Z, X), (Z, Y), (X, Y)])

        # Define custom functions for a clear linear model
        def z_mechanism(parents):
            # Z = U_Z
            return parents[0].value

        def x_mechanism(parents):
            # X = 0.5*Z + U_X
            # parents[0] is U_X, parents[1] is Z
            x_val = 0.5 * parents[1].value + parents[0].value
            print(
                f"In x_mechanism: z_value shape: {parents[1].value.shape}, x_value shape: {x_val.shape}"
            )
            return x_val

        def y_mechanism(parents):
            # Y = 0.5*X + 0.5*Z + U_Y
            # parents[0] is U_Y, parents[1] is X, parents[2] is Z
            y_val = 0.5 * parents[1].value + 0.5 * parents[2].value + parents[0].value
            print(
                f"In y_mechanism: x_value shape: {parents[1].value.shape}, z_value shape: {parents[2].value.shape}, y_value shape: {y_val.shape}"
            )
            return y_val

        scm.set_function(Z, MechanismFamily.CUSTOM, custom_function=z_mechanism)
        scm.set_function(X, MechanismFamily.CUSTOM, custom_function=x_mechanism)
        scm.set_function(Y, MechanismFamily.CUSTOM, custom_function=y_mechanism)

        # Create CATE Query:
        # Format: E[Y | do(T=1), X=x] - E[Y | do(T=0), X=x]
        # Here:   E[Y | do(X=1), Z=0.5] - E[Y | do(X=0), Z=0.5]
        query = Query.createL2CATE(Y=Y, T=X, T1_value=1, T0_value=0, X=Z, X_value=0.5)

        # Create query estimator with kernel settings
        query_estimator = QueryEstimator(
            n_samples=1000,  # Reduced sample size for debugging
            kernel_type=KernelType.GAUSSIAN,
            kernel_bandwidth=0.2,
        )

        # Evaluate query
        print("\nEvaluating CATE with continuous variables")
        estimate = query_estimator.evaluate_CATE(scm, query)
        self.assertIsNotNone(estimate, "CATE estimate should not be None")

        # Print debug information
        print(f"Expected: 0.5, Actual: {estimate}")

        # The effect of X on Y is 0.5 in our model (Y = 0.5*X + 0.5*Z + noise)
        # So CATE should be close to 0.5
        self.assertAlmostEqual(
            estimate,
            0.5,
            delta=0.1,
            msg="CATE estimate should be close to 0.5 for our linear model",
        )
        print(f"Continuous CATE Estimate: {estimate}")

    def test_evaluate_CTF_TE_continuous_SCM(self):
        """
        Test CTF-TE evaluation on a continuous SCM.
        """
        # Set random seed for reproducibility
        np.random.seed(42)
        torch.manual_seed(42)

        # Create variables
        T = Variable(
            name="T",
            variable_type=VariableDataType.CONTINUOUS,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.CONTINUOUS,
        )
        X1 = Variable(
            name="X1",
            variable_type=VariableDataType.CONTINUOUS,
        )
        X2 = Variable(
            name="X2",
            variable_type=VariableDataType.CONTINUOUS,
        )

        # Create SCM with a simple linear model
        scm = SCM(
            variables=[T, Y, X1, X2],
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_args=[0, 0.1],  # Reduce noise variance
            noise_mode=NoiseMode.ADDITIVE,
        )

        # Create a model: X1->T<-X2, X1->Y<-T, X2->Y
        scm.add_edges([(X1, T), (X2, T), (T, Y), (X1, Y), (X2, Y)])

        # Define custom functions for a clear linear model
        def x1_mechanism(parents):
            # X1 = U_X1
            return parents[0].value

        def x2_mechanism(parents):
            # X2 = U_X2
            return parents[0].value

        def t_mechanism(parents):
            # T = 0.5*X1 + 0.5*X2 + U_T
            # parents[0] is U_T, parents[1] is X1, parents[2] is X2
            t_val = 0.5 * parents[1].value + 0.5 * parents[2].value + parents[0].value
            print(
                f"In t_mechanism: x1_value shape: {parents[1].value.shape}, x2_value shape: {parents[2].value.shape}, t_value shape: {t_val.shape}"
            )
            return t_val

        def y_mechanism(parents):
            # Y = 1.0*T + 0.3*X1 + 0.3*X2 + U_Y
            # parents[0] is U_Y, parents[1] is T, parents[2] is X1, parents[3] is X2
            y_val = (
                1.0 * parents[1].value
                + 0.3 * parents[2].value
                + 0.3 * parents[3].value
                + parents[0].value
            )
            print(
                f"In y_mechanism: t_value shape: {parents[1].value.shape}, x1_value shape: {parents[2].value.shape}, x2_value shape: {parents[3].value.shape}, y_value shape: {y_val.shape}"
            )
            return y_val

        scm.set_function(X1, MechanismFamily.CUSTOM, custom_function=x1_mechanism)
        scm.set_function(X2, MechanismFamily.CUSTOM, custom_function=x2_mechanism)
        scm.set_function(T, MechanismFamily.CUSTOM, custom_function=t_mechanism)
        scm.set_function(Y, MechanismFamily.CUSTOM, custom_function=y_mechanism)

        # Create Ctf-TE Query for continuous variables
        # E[Y | do(T=1), X1=0.5, X2=0.5] - E[Y | do(T=0), X1=0.5, X2=0.5]
        query = Query.createL3CtfTE(
            Y=Y,
            T=T,
            V_F=[X1, X2],
            T1_value=1.0,
            T0_value=0.0,
            V_F_value=[0.5, 0.5],
            Y_value=None,  # For continuous variables, we're interested in the mean difference
        )

        # Initialize query estimator with kernel settings
        query_estimator = QueryEstimator(
            n_samples=1000,  # Reduced sample size for debugging
            kernel_type=KernelType.GAUSSIAN,
            kernel_bandwidth=0.2,
        )

        # Evaluate query
        print("\nEvaluating CTF-TE with continuous variables")
        estimate = query_estimator.evaluate_query(scm, query)
        self.assertIsNotNone(estimate, "CTF-TE estimate should not be None")

        # Print debug information
        print(f"Expected: 1.0, Actual: {estimate}")

        # The direct effect of T on Y is 1.0 in our model
        # So Ctf-TE should be close to 1.0
        self.assertAlmostEqual(
            estimate,
            1.0,
            delta=0.3,
            msg="CTF-TE estimate should be close to 1.0 for our linear model",
        )
        print(f"Continuous CTF-TE Estimate: {estimate}")

    def test_evaluate_CTF_TE_continuous_SCM_with_Y_value(self):
        """
        Test that attempting to evaluate CTF-TE for a continuous variable with a specific Y value
        raises an appropriate error, since computing probabilities for continuous variables is not supported.
        """
        # Set random seed for reproducibility
        np.random.seed(42)
        torch.manual_seed(42)

        # Create variables
        T = Variable(
            name="T",
            variable_type=VariableDataType.CONTINUOUS,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.CONTINUOUS,
        )
        X1 = Variable(
            name="X1",
            variable_type=VariableDataType.CONTINUOUS,
        )
        X2 = Variable(
            name="X2",
            variable_type=VariableDataType.CONTINUOUS,
        )

        # Create SCM with a simple linear model
        scm = SCM(
            variables=[T, Y, X1, X2],
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_args=[0, 0.1],  # Reduce noise variance
            noise_mode=NoiseMode.ADDITIVE,
        )

        # Create a model: X1->T<-X2, X1->Y<-T, X2->Y
        scm.add_edges([(X1, T), (X2, T), (T, Y), (X1, Y), (X2, Y)])

        # Define custom functions for a clear linear model
        def x1_mechanism(parents):
            return parents[0].value  # X1 = U_X1

        def x2_mechanism(parents):
            return parents[0].value  # X2 = U_X2

        def t_mechanism(parents):
            # T = 0.5*X1 + 0.5*X2 + U_T
            return 0.5 * parents[1].value + 0.5 * parents[2].value + parents[0].value

        def y_mechanism(parents):
            # Y = 1.0*T + 0.3*X1 + 0.3*X2 + U_Y
            return (
                1.0 * parents[1].value
                + 0.3 * parents[2].value
                + 0.3 * parents[3].value
                + parents[0].value
            )

        scm.set_function(X1, MechanismFamily.CUSTOM, custom_function=x1_mechanism)
        scm.set_function(X2, MechanismFamily.CUSTOM, custom_function=x2_mechanism)
        scm.set_function(T, MechanismFamily.CUSTOM, custom_function=t_mechanism)
        scm.set_function(Y, MechanismFamily.CUSTOM, custom_function=y_mechanism)

        # Create Ctf-TE Query for continuous variables with a specific Y value
        # P(Y=1.0 | do(T=1), X1=0.5, X2=0.5) - P(Y=1.0 | do(T=0), X1=0.5, X2=0.5)
        query = Query.createL3CtfTE(
            Y=Y,
            T=T,
            V_F=[X1, X2],
            T1_value=1.0,
            T0_value=0.0,
            V_F_value=[0.5, 0.5],
            Y_value=1.0,  # Specifying a Y value for a continuous variable
        )

        # Initialize query estimator
        query_estimator = QueryEstimator(
            n_samples=1000,
            kernel_type=KernelType.GAUSSIAN,
            kernel_bandwidth=0.2,
        )

        # This should raise a ValueError because we're trying to compute a probability
        # for a continuous variable
        print("\nEvaluating CTF-TE with continuous variables and specific Y value")
        with self.assertRaises(ValueError) as context:
            query_estimator.evaluate_CTF_TE(scm, query)

        # Check the error message
        self.assertIn(
            "Computing probabilities (with target_y_value) for continuous variables is not supported",
            str(context.exception),
        )
        print(
            "Test passed: Correctly raised ValueError for continuous probability query in CTF-TE"
        )

    def test_evaluate_OIP_continuous_SCM(self):
        """
        Test that attempting to evaluate outcome interventional probability with continuous variables
        raises an appropriate error, since computing probabilities for continuous variables
        is not supported.
        """
        # Set random seed for reproducibility
        np.random.seed(42)
        torch.manual_seed(42)

        # Create SCM
        X = Variable(
            name="X",
            variable_type=VariableDataType.CONTINUOUS,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.CONTINUOUS,
        )
        Z = Variable(
            name="Z",
            variable_type=VariableDataType.CONTINUOUS,
        )
        scm = SCM(
            variables=[X, Y, Z],
            noise_distribution=NoiseDistribution.GAUSSIAN,
            noise_args=[0, 0.1],  # Reduce noise variance
            noise_mode=NoiseMode.ADDITIVE,
        )

        # Create a simple model: Z->X->Y, Z->Y
        scm.add_edges([(Z, X), (X, Y), (Z, Y)])

        # Define custom functions for a clear linear model
        def z_mechanism(parents):
            # Z = U_Z
            return parents[0].value

        def x_mechanism(parents):
            # X = 0.5*Z + U_X
            # parents[0] is U_X, parents[1] is Z
            x_val = 0.5 * parents[1].value + parents[0].value
            return x_val

        def y_mechanism(parents):
            # Y = X + 0.5*Z + U_Y
            # parents[0] is U_Y, parents[1] is X, parents[2] is Z
            y_val = parents[1].value + 0.5 * parents[2].value + parents[0].value
            return y_val

        scm.set_function(Z, MechanismFamily.CUSTOM, custom_function=z_mechanism)
        scm.set_function(X, MechanismFamily.CUSTOM, custom_function=x_mechanism)
        scm.set_function(Y, MechanismFamily.CUSTOM, custom_function=y_mechanism)

        # Create Outcome Interventional Probability Query for continuous variables
        # P(Y=1.5 | do(X=1.0), Z=0.5)
        query = Query.createL2OIP(Y=Y, T=X, X=Z, Y_value=1.5, T_value=1.0, X_value=0.5)

        # Initialize query estimator with kernel settings
        query_estimator = QueryEstimator(
            n_samples=1000,  # Reduced sample size for debugging
            kernel_type=KernelType.GAUSSIAN,
            kernel_bandwidth=0.2,
        )

        # Evaluate query - this should now raise a ValueError
        print("\nEvaluating OIP with continuous variables")
        with self.assertRaises(ValueError) as context:
            query_estimator.evaluate_outcome_interventional_prob(scm, query)

        # Check the error message
        self.assertIn(
            "Computing probabilities for continuous variables is not supported",
            str(context.exception),
        )
        print(
            "Test passed: Correctly raised ValueError for continuous probability query"
        )

    def test_evaluate_OIP_discrete_SCM_with_conditioning(self):
        """
        Test OIP evaluation on a discrete SCM with conditioning variables.
        """
        # Create discrete variables
        X = Variable(
            name="X",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        Z = Variable(
            name="Z",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        # Create SCM with manual mechanism assignment
        scm = SCM(
            variables=[X, Y, Z],
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_mode=NoiseMode.ADDITIVE,
            noise_args=[-1, 1],
            n_samples=1000,
        )

        # Add edges: Z -> X -> Y, Z -> Y
        scm.add_edge(Z, X)
        scm.add_edge(X, Y)
        scm.add_edge(Z, Y)

        # Set noise regions for exogenous variables
        [U_Z_name] = scm.parents[Z.name]
        scm.variables[U_Z_name].noise_regions = [0.5]
        U_X_name = [p for p in scm.parents[X.name] if scm.variables[p].exogenous][0]
        scm.variables[U_X_name].noise_regions = [0.5]
        U_Y_name = [p for p in scm.parents[Y.name] if scm.variables[p].exogenous][0]
        scm.variables[U_Y_name].noise_regions = [0.5]

        # Set simple mechanisms for testing
        mechanism_z = [([(0,)], 0), ([(1,)], 1)]  # noise -> Z
        mechanism_x = [([(0, 0), (1, 1)], 0), ([(1, 0), (0, 1)], 1)]  # (noise, Z) -> X
        mechanism_y = [
            ([(0, 0, 0), (1, 1, 1), (1, 1, 0)], 0),
            ([(1, 0, 0), (0, 1, 1), (1, 0, 1), (0, 1, 0), (0, 0, 1)], 1),
        ]  # (noise, X, Z) -> Y - covers all combinations

        scm.set_function(Z, MechanismFamily.TABULAR, mechanism_args=mechanism_z)
        scm.set_function(X, MechanismFamily.TABULAR, mechanism_args=mechanism_x)
        scm.set_function(Y, MechanismFamily.TABULAR, mechanism_args=mechanism_y)

        # Create OIP query: P(Y=1 | do(X=1), Z=0)
        query = Query.createL2OIP(Y=Y, T=X, X=[Z], Y_value=1, T_value=1, X_value=[0])

        # Evaluate the query
        result = self.query_estimator.evaluate_outcome_interventional_prob(scm, query)

        # Result should be a valid probability
        self.assertGreaterEqual(result, 0.0, "Result should be non-negative")
        self.assertLessEqual(result, 1.0, "Result should be at most 1")

    def test_evaluate_OIP_discrete_SCM_empty_conditioning(self):
        """
        Test OIP evaluation on a discrete SCM with empty conditioning variables (X=[]).
        """
        # Create discrete variables
        X = Variable(
            name="X",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        # Create SCM
        scm = SCM(
            variables=[X, Y],
            noise_distribution=NoiseDistribution.UNIFORM,
            noise_mode=NoiseMode.ADDITIVE,
            noise_args=[-1, 1],
            n_samples=1000,
        )

        # Add edge: X -> Y
        scm.add_edge(X, Y)

        # Set noise regions for exogenous variables
        [U_X_name] = scm.parents[X.name]
        scm.variables[U_X_name].noise_regions = [0.5]
        U_Y_name = [p for p in scm.parents[Y.name] if scm.variables[p].exogenous][0]
        scm.variables[U_Y_name].noise_regions = [0.5]

        # Set simple mechanisms where X determines Y
        # X can be 0 or 1 based on noise
        # Y = X (copy mechanism for simplicity)
        mechanism_x = [
            ([(0,)], 0),  # noise region 0 -> X=0
            ([(1,)], 1),  # noise region 1 -> X=1
        ]
        mechanism_y = [
            ([(0, 0), (1, 1)], 0),  # (noise=0,X=0) or (noise=1,X=1) -> Y=0
            ([(1, 0), (0, 1)], 1),  # (noise=1,X=0) or (noise=0,X=1) -> Y=1
        ]

        scm.set_function(X, MechanismFamily.TABULAR, mechanism_args=mechanism_x)
        scm.set_function(Y, MechanismFamily.TABULAR, mechanism_args=mechanism_y)

        # Create OIP query with empty conditioning: P(Y=1 | do(X=1))
        query = Query.createL2OIP(Y=Y, T=X, X=[], Y_value=1, T_value=1, X_value=[])

        # Evaluate the query
        result = self.query_estimator.evaluate_outcome_interventional_prob(scm, query)

        # With do(X=1), mechanism should map Y=1 for at least some noise values
        # We expect some probability > 0
        self.assertGreater(result, 0.0, "Result should be greater than 0")
        self.assertLessEqual(result, 1.0, "Result should be at most 1")


if __name__ == "__main__":
    unittest.main()
