from typing import Callable, Dict, List, Tuple, Union

import numpy as np

from .constants import ErrorMetric
from .query import Query
from .sampler import Sampler
from .space_of_interest import SpaceOfInterest


class CausalProfiler:
    def __init__(
        self,
        space_of_interest: SpaceOfInterest,
        metric: Union[
            str, ErrorMetric, Callable[[np.ndarray, np.ndarray], float]
        ] = ErrorMetric.L2,
        return_adjacency_matrix: bool = False,
        n_samples=10000,
    ):
        """
        Initialize the CausalProfiler.

        Args:
            space_of_interest (SpaceOfInterest): The space of interest from which to sample SCMs and queries.
            metric (Union[str, ErrorMetric, Callable[[np.ndarray, np.ndarray], float]]):
                The error metric to evaluate the difference between estimated query results and true query results.
                This can be:
                - An ErrorMetric enum value (preferred).
                - A string representing a predefined ErrorMetric ('L1', 'L2', 'MSE', 'MAPE', 'HAMMING', 'COSINE').
                - A custom callable function that takes (predicted_values, actual_values) and returns a float.
            return_adjacency_matrix (bool): If True, returns the adjacency matrix of the sampled SCM. Otherwise, returns adjacency list.
            n_samples (int): Number of samples for queries evaluation.

        Returns:
            None
        """
        self.sampler = Sampler(
            space_of_interest=space_of_interest,
            return_adjacency_matrix=return_adjacency_matrix,
            n_samples=n_samples,
        )
        if isinstance(metric, str):
            metric = ErrorMetric(metric)
        self.metric = metric

    def set_metric(self, metric):
        self.metric = metric

    def generate_samples_and_queries(
        self,
    ) -> Tuple[
        Dict[str, np.ndarray],
        Tuple[List[Query], List[float]],
        Union[Dict[str, List[str]], np.ndarray],
    ]:
        return self.sampler.generate_samples_and_queries()

    def evaluate_error(
        self,
        estimated: List[float],
        target: List[float],
    ) -> Tuple[float, int]:
        """
        Evaluate error/distance between predicted and actual query estimates.

        Args:
            estimated: a list of floats [E1',E2',...,EN'] of user estimates. Some might be NaN.
                       Can also be [(Q, E), ...], in which case Q is ignored and E is extracted.
            target: a list of floats [E1,...,EN] representing the true query values.

        Returns:
            (error, num_failed):
                error (float): The computed error based on non-NaN predicted values.
                num_failed (int): The count of failed predictions (where predicted is NaN).

        Note:
            If all predictions are NaN, error = 0.0 and num_failed = len(estimated).
        """
        # Extract predicted values if they come as (Q, E)
        if len(target) == 0:
            raise ValueError("Predicted list is empty.")
        if isinstance(estimated[0], tuple):
            # means predicted is [(Q, E), ...]
            pred_values = [pe[1] for pe in estimated]
        else:
            # predicted is already [E1, E2, ...]
            pred_values = estimated

        pred_values = np.array(pred_values, dtype=float)
        actual_values = np.array(target, dtype=float)

        if pred_values.shape != actual_values.shape:
            raise ValueError("predicted and actual must have the same length.")

        # Count how many are NaN
        nan_mask = np.isnan(pred_values)
        num_failed = np.sum(nan_mask)

        if np.any(nan_mask):
            # Filter out NaNs for the error computation
            pred_values = pred_values[~nan_mask]
            actual_values = actual_values[~nan_mask]

        if len(pred_values) == 0:
            # All failed
            return 0.0, num_failed

        # Get the error for the non-Nan estimates
        if callable(self.metric):
            error = self.metric(pred_values, actual_values)

        elif self.metric == ErrorMetric.L1:
            # Mean L1 distance
            error = np.mean(np.abs(pred_values - actual_values))

        elif self.metric == ErrorMetric.L2:
            # Mean L2 (Euclidean) distance
            # L2 can be interpreted as sqrt of mean squared error
            error = np.sqrt(np.mean((pred_values - actual_values) ** 2))

        elif self.metric == ErrorMetric.MSE:
            error = np.mean((pred_values - actual_values) ** 2)

        elif self.metric == ErrorMetric.MAPE:
            # MAPE = mean(|(pred - actual)/actual|)*100
            # Need to handle division by zero
            denom = actual_values.copy()
            denom[denom == 0] = 1e-10  # small constant to avoid division by zero
            error = np.mean(np.abs((pred_values - actual_values) / denom)) * 100

        elif self.metric == ErrorMetric.HAMMING:
            # Hamming distance: fraction of positions where predictions differ from actual
            error = np.mean(pred_values != actual_values)

        elif self.metric == ErrorMetric.COSINE:
            # Cosine distance = 1 - cosine similarity
            # cosine similarity = dot(a,b)/(||a||*||b||)
            dot = np.dot(pred_values, actual_values)
            norm_a = np.linalg.norm(pred_values)
            norm_b = np.linalg.norm(actual_values)
            if norm_a == 0 or norm_b == 0:
                # If either vector is zero vector, cosine distance could be defined as 1
                # because they are orthogonal (or undefined)
                error = 1.0
            else:
                cosine_similarity = dot / (norm_a * norm_b)
                error = 1.0 - cosine_similarity

        else:
            raise ValueError(f"Unknown error metric: {self.metric}")

        return error, num_failed
