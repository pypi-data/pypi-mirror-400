from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

from .constants import KernelType, QueryType, VariableDataType
from .kernels import get_kernel_function
from .query import Query
from .scm import SCM
from .variable import Variable


class QueryEstimator:
    def __init__(
        self,
        n_samples,
        store_raw_data=False,
        kernel_type=KernelType.GAUSSIAN,
        kernel_bandwidth=0.1,
        kernel_fn=None,
    ):
        """
        n_samples: int
            How many samples to use to estimate a query
        store_raw_data: bool
            Whether to store in the class the data used to compute a query:
            ONLY supported for interventional probabilities (used in verification)
            TODO: this is easy to extend to all queries
        kernel_type: KernelType
            Only needed for continuous variables
            Type of kernel to use for continuous variables
        kernel_bandwidth: float
            Only needed for continuous variables
            Bandwidth for kernel density estimation
        kernel_fn: callable, optional
            Only needed for continuous variables
            Custom kernel function for weighting. If provided, overrides kernel_type
        """
        self.n_samples = n_samples
        self.store_raw_data = store_raw_data
        self.raw_data = {}  # Dictionary to store raw data for each query
        self.kernel_type = kernel_type
        self.kernel_bandwidth = kernel_bandwidth
        self.kernel_fn = kernel_fn

    def get_kernel_function(self) -> Callable:
        """
        Returns the appropriate kernel function based on kernel_type or the custom kernel_fn.
        """
        return get_kernel_function(self.kernel_type, self.kernel_fn)

    def reset_and_sample(self, scm: SCM, reset_noise: bool = True):
        """
        Resets the SCM values and samples noise variables if specified.
        """
        # This specifies the number of samples that the SCM should use in the batch_dimension of the variables
        scm.n_samples = self.n_samples
        scm.reset_values(reset_noise=reset_noise)
        if reset_noise:
            scm.sample_noise_variables()

    def compute_data(self, scm: SCM) -> Dict[str, np.ndarray]:
        """
        Computes all variables in the SCM and collects their values.
        """
        scm.compute_variables()
        return {var_id: var.value for var_id, var in scm.variables.items()}

    def filter_data(
        self,
        data: Dict[str, np.ndarray],
        variables: List[Variable],
        target_values: List[Any],
        return_weights: bool = False,
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Filters data points to match specified conditions.
        For discrete variables, uses exact matching.
        For continuous variables, uses kernel weighting.

        Args:
            data: Dictionary mapping variable IDs to their values
            variables: List of variables to filter on
            target_values: Target values for filtering
            return_weights: If True, returns both the mask and the weights

        Returns:
            If return_weights is False:
                A boolean mask of shape (n_samples,)
            If return_weights is True:
                A tuple (mask, weights) where:
                    - mask is a boolean array of shape (n_samples,)
                    - weights is a float array of shape (n_samples,) with kernel weights
        """
        # Start with all samples included
        mask = np.ones(self.n_samples, dtype=bool)
        weights = np.ones(self.n_samples)

        # Get the kernel function for continuous variables
        kernel_fn = self.get_kernel_function()

        for variable, target_value in zip(variables, target_values):
            variable_id = variable.name

            if variable.variable_type == VariableDataType.DISCRETE:
                # For discrete variables, use exact matching
                mask &= np.all(data[variable_id] == target_value, axis=1)
            else:
                # For continuous variables, compute kernel weights
                var_values = data[variable_id]
                kernel_weights = kernel_fn(
                    var_values, target_value, self.kernel_bandwidth
                )

                # Update the weights
                weights *= kernel_weights

                # Update mask (consider points with non-zero weights)
                mask &= kernel_weights > 1e-10

        if return_weights:
            return mask, weights
        else:
            return mask

    def clear_raw_data(self):
        """
        Clears all stored raw data.
        """
        self.raw_data = {}

    def set_store_raw_data(self, value: bool):
        """
        Sets the store_raw_data flag and clears raw data if setting to False.
        """
        if not value and self.store_raw_data:
            self.clear_raw_data()
        self.store_raw_data = value

    def evaluate_ATE(self, scm: SCM, query: Query):
        """
        Evaluates the Average Treatment Effect (ATE).
        E[Y | do(T=t1)] - E[Y | do(T=t0)]

        Works for both discrete and continuous variables.
        """
        self.reset_and_sample(scm)

        # Do(T1)
        scm.do_hard_interventions(query.vars["T"], query.vars_values["T"][0])
        data_t1 = self.compute_data(scm)
        scm.remove_interventions(query.vars["T"])

        # Do(T0)
        self.reset_and_sample(scm, reset_noise=False)
        scm.do_hard_interventions(query.vars["T"], query.vars_values["T"][1])
        data_t0 = self.compute_data(scm)

        # Remove intervention otherwise the variable will never be able to be reset.
        scm.remove_interventions(query.vars["T"])

        # Compute ATE
        Y_variable_id = query.vars["Y"][0].name
        # ATE works the same for both discrete and continuous variables
        return np.nanmean(data_t1[Y_variable_id]) - np.nanmean(data_t0[Y_variable_id])

    def evaluate_conditional(self, scm: SCM, query: Query):
        """
        Evaluates conditional probability or statistics.
        P(Y=y | X=x) for discrete variables or E[Y | X=x] for continuous variables.

        For continuous Y variables, target_y_value must be None (to compute expectation).
        Computing probabilities for specific values is not supported for continuous variables.
        """
        self.reset_and_sample(scm)
        data = self.compute_data(scm)
        Y_variable = query.vars["Y"][0]
        y_variable_id = Y_variable.name
        target_y_value = query.vars_values["Y"][0]

        # For continuous variables with a specific target value, probability calculation doesn't make sense
        if (
            Y_variable.variable_type == VariableDataType.CONTINUOUS
            and target_y_value is not None
        ):
            raise ValueError(
                "Computing probabilities (with target_y_value) for continuous variables is not supported. "
                "For continuous variables, only expectations can be computed (target_y_value should be None)."
            )

        # Get values and weights for conditioning
        mask, weights = self.filter_data(
            data, query.vars["X"], query.vars_values["X"], return_weights=True
        )

        if not np.any(mask):
            return np.nan

        # Get Y values for samples that passed the filter
        y_values = data[y_variable_id][mask]
        sample_weights = weights[mask]

        # Normalize weights
        if np.sum(sample_weights) > 0:
            sample_weights = sample_weights / np.sum(sample_weights)

        if Y_variable.variable_type == VariableDataType.DISCRETE:
            # For discrete Y: compute weighted proportion for target Y value
            # Handle multidimensional arrays correctly
            matches = (
                np.all(y_values == target_y_value, axis=1)
                if y_values.ndim > 1
                else (y_values == target_y_value)
            )
            return np.sum(sample_weights[matches])
        else:
            # For continuous Y: compute weighted mean (target_y_value must be None at this point)
            if y_values.ndim > 1:
                # For multidimensional y_values, compute weighted mean per dimension
                weighted_mean = np.zeros(y_values.shape[1])
                for i in range(y_values.shape[1]):
                    weighted_mean[i] = np.sum(y_values[:, i] * sample_weights)
                return weighted_mean[0]  # Return first dimension for now
            else:
                # For 1D y_values
                return np.sum(y_values * sample_weights)

    def evaluate_CATE(self, scm: SCM, query: Query):
        """
        Evaluates the Conditional Average Treatment Effect (CATE).
        E[Y | do(T=t1), X=x] - E[Y | do(T=t0), X=x]

        Works for both discrete and continuous variables.
        """
        self.reset_and_sample(scm)
        Y_variable = query.vars["Y"][0]
        Y_variable_id = Y_variable.name

        # Do(T1) and filter by X
        scm.do_hard_interventions(query.vars["T"], query.vars_values["T"][0])
        data_t1 = self.compute_data(scm)
        mask_t1, weights_t1 = self.filter_data(
            data_t1, query.vars["X"], query.vars_values["X"], return_weights=True
        )

        if not np.any(mask_t1):
            scm.remove_interventions(query.vars["T"])
            return np.nan

        # Normalize weights
        weights_t1_norm = weights_t1[mask_t1]
        if np.sum(weights_t1_norm) > 0:
            weights_t1_norm = weights_t1_norm / np.sum(weights_t1_norm)

        # Get Y values
        y_values_t1 = data_t1[Y_variable_id][mask_t1]

        # Compute weighted average
        if y_values_t1.ndim > 1:
            # For multidimensional y_values, compute weighted mean per dimension
            avg_t1 = 0
            for i in range(y_values_t1.shape[1]):
                avg_t1 += (
                    np.sum(y_values_t1[:, i] * weights_t1_norm) / y_values_t1.shape[1]
                )
        else:
            avg_t1 = np.sum(y_values_t1 * weights_t1_norm)

        scm.remove_interventions(query.vars["T"])

        # Do(T0) and filter by X
        self.reset_and_sample(scm, reset_noise=False)
        scm.do_hard_interventions(query.vars["T"], query.vars_values["T"][1])
        data_t0 = self.compute_data(scm)
        mask_t0, weights_t0 = self.filter_data(
            data_t0, query.vars["X"], query.vars_values["X"], return_weights=True
        )

        if not np.any(mask_t0):
            scm.remove_interventions(query.vars["T"])
            return np.nan

        # Normalize weights
        weights_t0_norm = weights_t0[mask_t0]
        if np.sum(weights_t0_norm) > 0:
            weights_t0_norm = weights_t0_norm / np.sum(weights_t0_norm)

        # Get Y values
        y_values_t0 = data_t0[Y_variable_id][mask_t0]

        # Compute weighted average
        if y_values_t0.ndim > 1:
            # For multidimensional y_values, compute weighted mean per dimension
            avg_t0 = 0
            for i in range(y_values_t0.shape[1]):
                avg_t0 += (
                    np.sum(y_values_t0[:, i] * weights_t0_norm) / y_values_t0.shape[1]
                )
        else:
            avg_t0 = np.sum(y_values_t0 * weights_t0_norm)

        # Remove intervention otherwise the variable will never be able to be reset.
        scm.remove_interventions(query.vars["T"])

        # Compute CATE
        return avg_t1 - avg_t0

    def compute_counterfactuals(
        self, scm: SCM, exogenous_realizations: Dict[str, Any], target_variable_id: str
    ):
        """
        Computes the target variable given exogenous realizations.
        """
        # Set the exogenous variables to the stored exogenous realizations
        for noise_var_name, values in exogenous_realizations.items():
            noise_var = scm.variables[noise_var_name]
            noise_var.value = values  # Set values for all samples

        # Reset variable values except noise variables
        scm.reset_values(reset_noise=False)
        # Compute variables
        scm.compute_variables()
        # Get the target variable values
        target_values = scm.variables[target_variable_id].value
        return target_values

    def evaluate_CTF_TE(self, scm: SCM, query: Query):
        """
        Evaluates the Counterfactual Total Effect (Ctf-TE).
        P(Y=y_{do(T=t1)} | V_F=v_F) - P(Y=y_{do(T=t0)} | V_F=v_F)

        For discrete variables: Computes the difference in probabilities.
        For continuous variables: Computes the difference in expectations (only when target_y_value is None).
        """
        # Temporarily store and restore the n_samples because it might change
        # depending on how many samples the QueryEstimator uses
        scm_samples = scm.n_samples

        # Target Y variable and target Y value
        Y_variable = query.vars["Y"][0]
        Y_variable_id = Y_variable.name
        target_y_value = query.vars_values["Y"][0]

        # For continuous variables with a specific target value, this doesn't make causal sense
        if (
            Y_variable.variable_type == VariableDataType.CONTINUOUS
            and target_y_value is not None
        ):
            raise ValueError(
                "Computing probabilities (with target_y_value) for continuous variables is not supported in CTF_TE. "
                "For continuous variables, only expectations can be computed (target_y_value should be None)."
            )

        # Step 1: Sample N observations from the original SCM
        self.reset_and_sample(scm)
        data = self.compute_data(scm)

        # Step 2: Keep observations where V_F = v_F and store exogenous realizations
        V_F_variables = query.vars["V_F"]
        V_F_values = query.vars_values["V_F"]
        mask, weights = self.filter_data(
            data, V_F_variables, V_F_values, return_weights=True
        )

        # If no observations match, return NaN or handle appropriately
        if not np.any(mask):
            return np.nan

        # Store exogenous realizations (noise variables) for the matching observations
        exogenous_realizations = {}
        for noise_var_name in scm.noise_variables:
            noise_var = scm.variables[noise_var_name]
            exogenous_realizations[noise_var_name] = noise_var.value[mask]

        # Also store the weights for matching observations
        sample_weights = weights[mask]

        # Normalize weights
        if np.sum(sample_weights) > 0:
            sample_weights = sample_weights / np.sum(sample_weights)

        # Shrink SCM to only consider the masked examples
        scm.n_samples = np.sum(mask)

        # Step 3: Modify the SCM with the intervention do(T=t)
        scm.do_hard_interventions(query.vars["T"], query.vars_values["T"][0])
        # Step 4: Compute Y under the intervention do(T=t) using exogenous realizations
        Y_values_t = self.compute_counterfactuals(
            scm, exogenous_realizations, Y_variable_id
        )
        # No need to remove intervention because we intervene on the same variable again

        # Step 5: Compute P(y_{do(T=t)} | V_F = v_F)
        if Y_variable.variable_type == VariableDataType.DISCRETE:
            # For discrete Y, compute weighted proportion
            matches = (
                np.all(Y_values_t == target_y_value, axis=1)
                if Y_values_t.ndim > 1
                else (Y_values_t == target_y_value)
            )
            P_t = np.sum(sample_weights[matches])
        else:
            # For continuous Y, use weighted mean (target_y_value should be None at this point)
            if Y_values_t.ndim > 1:
                # For multidimensional Y_values, compute weighted mean per dimension
                P_t = 0
                for i in range(Y_values_t.shape[1]):
                    P_t += (
                        np.sum(Y_values_t[:, i] * sample_weights) / Y_values_t.shape[1]
                    )
            else:
                P_t = np.sum(Y_values_t * sample_weights)

        # Step 6: Repeat steps 3 to 5 with do(T=c)
        scm.do_hard_interventions(query.vars["T"], query.vars_values["T"][1])
        Y_values_c = self.compute_counterfactuals(
            scm, exogenous_realizations, Y_variable_id
        )

        if Y_variable.variable_type == VariableDataType.DISCRETE:
            # For discrete Y, compute weighted proportion
            matches = (
                np.all(Y_values_c == target_y_value, axis=1)
                if Y_values_c.ndim > 1
                else (Y_values_c == target_y_value)
            )
            P_c = np.sum(sample_weights[matches])
        else:
            # For continuous Y, use weighted mean (target_y_value should be None at this point)
            if Y_values_c.ndim > 1:
                # For multidimensional Y_values, compute weighted mean per dimension
                P_c = 0
                for i in range(Y_values_c.shape[1]):
                    P_c += (
                        np.sum(Y_values_c[:, i] * sample_weights) / Y_values_c.shape[1]
                    )
            else:
                P_c = np.sum(Y_values_c * sample_weights)

        # Restore SCM to original sample size
        scm.n_samples = scm_samples
        # Remove intervention otherwise the variable will never be able to be reset.
        scm.remove_interventions(query.vars["T"])
        # Step 7: Return the difference
        return P_t - P_c

    def evaluate_outcome_interventional_prob(self, scm: SCM, query: Query):
        """
        Evaluates the probability of Y=y under the intervention do(T=t) and conditioned on X=x.
        P(Y=y | do(T=t), X=x)

        Works for discrete Y variables only. For continuous Y variables, only expectations
        (not specific values) can be computed, and that should be done using other query types.
        """
        # Get Y variable and value
        Y_variable = query.vars["Y"][0]
        Y_value = query.vars_values["Y"][0]

        # Check if Y is continuous, which is not supported for probability queries
        if Y_variable.variable_type == VariableDataType.CONTINUOUS:
            raise ValueError(
                "Computing probabilities for continuous variables is not supported. "
                "For continuous variables, use query types that compute expectations instead."
            )

        self.reset_and_sample(scm)

        # Apply intervention do(T=t)
        scm.do_hard_interventions(query.vars["T"], query.vars_values["T"])
        data = self.compute_data(scm)

        # Filter by X=x and get weights
        mask, weights = self.filter_data(
            data, query.vars["X"], query.vars_values["X"], return_weights=True
        )

        if not np.any(mask):
            scm.remove_interventions(query.vars["T"])
            return np.nan

        # Get Y values
        Y_variable_id = Y_variable.name
        Y_values = data[Y_variable_id][mask]

        # Get weights for the filtered samples
        sample_weights = weights[mask]

        # Normalize weights
        if np.sum(sample_weights) > 0:
            sample_weights = sample_weights / np.sum(sample_weights)

        # Store raw data if requested
        if self.store_raw_data:
            # Store only the latest data with a simple key
            query_key = f"{Y_variable_id}_{Y_value}"
            self.raw_data[query_key] = {
                "Y_values": Y_values,
                "Y_variable_id": Y_variable_id,
                "Y_value": Y_value,
                "weights": sample_weights,
            }

        # Remove the intervention otherwise the variable will never be able to be reset
        scm.remove_interventions(query.vars["T"])

        # For discrete variables, compute the weighted proportion
        # Handle multidimensional arrays correctly
        matches = (
            np.all(Y_values == Y_value, axis=1)
            if Y_values.ndim > 1
            else (Y_values == Y_value)
        )
        return np.sum(sample_weights[matches])

    def evaluate_query(self, scm: SCM, query: Query):
        if query.type == QueryType.ATE:
            return self.evaluate_ATE(scm, query)
        elif query.type == QueryType.CONDITIONAL:
            return self.evaluate_conditional(scm, query)
        elif query.type == QueryType.CATE:
            return self.evaluate_CATE(scm, query)
        elif query.type == QueryType.CTF_TE:
            return self.evaluate_CTF_TE(scm, query)
        elif query.type == QueryType.OIP:
            return self.evaluate_outcome_interventional_prob(scm, query)
        else:
            raise ValueError(f"Unsupported query type {query.type}")
