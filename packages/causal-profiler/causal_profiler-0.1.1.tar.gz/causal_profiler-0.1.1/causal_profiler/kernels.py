"""
Kernel functions for density estimation and weighting in causal inference.
"""

from typing import Callable

import numpy as np

from .constants import KernelType


def gaussian_kernel(x: np.ndarray, target: np.ndarray, bandwidth: float) -> np.ndarray:
    """
    Computes Gaussian kernel weights for points x relative to target.

    Args:
        x: Array of shape (n_samples, dimensionality)
        target: Array of shape (dimensionality,)
        bandwidth: Kernel bandwidth parameter

    Returns:
        Weights for each sample in x, shape (n_samples,)
    """
    # Ensure target is broadcastable
    target = np.atleast_1d(target)
    if target.ndim == 1:
        target = target.reshape(1, -1)

    # Compute squared distance
    sq_dist = np.sum(((x - target) / bandwidth) ** 2, axis=1)

    # Compute and return kernel weights
    return np.exp(-0.5 * sq_dist)


def uniform_kernel(x: np.ndarray, target: np.ndarray, bandwidth: float) -> np.ndarray:
    """
    Computes uniform kernel weights (1 if within bandwidth, 0 otherwise).

    Args:
        x: Array of shape (n_samples, dimensionality)
        target: Array of shape (dimensionality,)
        bandwidth: Kernel bandwidth parameter

    Returns:
        Weights for each sample in x, shape (n_samples,)
    """
    # Ensure target is broadcastable
    target = np.atleast_1d(target)
    if target.ndim == 1:
        target = target.reshape(1, -1)

    # Compute distance
    dist = np.sqrt(np.sum(((x - target) / bandwidth) ** 2, axis=1))

    # Return 1 if within bandwidth, 0 otherwise
    return (dist <= 1.0).astype(float)


def epanechnikov_kernel(
    x: np.ndarray, target: np.ndarray, bandwidth: float
) -> np.ndarray:
    """
    Computes Epanechnikov kernel weights.

    Args:
        x: Array of shape (n_samples, dimensionality)
        target: Array of shape (dimensionality,)
        bandwidth: Kernel bandwidth parameter

    Returns:
        Weights for each sample in x, shape (n_samples,)
    """
    # Ensure target is broadcastable
    target = np.atleast_1d(target)
    if target.ndim == 1:
        target = target.reshape(1, -1)

    # Compute squared distance
    sq_dist = np.sum(((x - target) / bandwidth) ** 2, axis=1)

    # Apply Epanechnikov kernel formula: K(u) = 0.75 * (1 - u²) for |u| <= 1
    weights = np.zeros_like(sq_dist)
    mask = sq_dist <= 1.0
    weights[mask] = 0.75 * (1 - sq_dist[mask])

    return weights


def triangular_kernel(
    x: np.ndarray, target: np.ndarray, bandwidth: float
) -> np.ndarray:
    """
    Computes triangular kernel weights.

    Args:
        x: Array of shape (n_samples, dimensionality)
        target: Array of shape (dimensionality,)
        bandwidth: Kernel bandwidth parameter

    Returns:
        Weights for each sample in x, shape (n_samples,)
    """
    # Ensure target is broadcastable
    target = np.atleast_1d(target)
    if target.ndim == 1:
        target = target.reshape(1, -1)

    # Compute distance
    dist = np.sqrt(np.sum(((x - target) / bandwidth) ** 2, axis=1))

    # Apply triangular kernel formula: K(u) = (1 - |u|) for |u| <= 1
    weights = np.zeros_like(dist)
    mask = dist <= 1.0
    weights[mask] = 1.0 - dist[mask]

    return weights


def epsilon_kernel(x: np.ndarray, target: np.ndarray, epsilon: float) -> np.ndarray:
    """
    Computes epsilon-based matching weights (1 if |x-target| < epsilon, 0 otherwise).
    This is essentially a boxcar/uniform kernel that uses the raw distance rather than
    normalized distance.

    Args:
        x: Array of shape (n_samples, dimensionality)
        target: Array of shape (dimensionality,)
        epsilon: Threshold distance for matching (bandwidth parameter)

    Returns:
        Weights for each sample in x, shape (n_samples,)
    """
    # Ensure target is broadcastable
    target = np.atleast_1d(target)
    if target.ndim == 1:
        target = target.reshape(1, -1)

    # Check if each dimension is within epsilon of the target
    # For multidimensional data, only return 1 if ALL dimensions are within epsilon
    within_epsilon = np.all(np.abs(x - target) < epsilon, axis=1)

    # Convert boolean array to float (1.0 or 0.0)
    return within_epsilon.astype(float)


def get_kernel_function(
    kernel_type: KernelType, custom_kernel_fn: Callable = None
) -> Callable:
    """
    Returns the appropriate kernel function based on kernel_type or the custom kernel_fn.

    Args:
        kernel_type: Type of kernel to use
        custom_kernel_fn: Optional custom kernel function

    Returns:
        The appropriate kernel function

    Raises:
        ValueError: If an unsupported kernel type is provided
    """

    kernel_functions = {
        KernelType.GAUSSIAN: gaussian_kernel,
        KernelType.UNIFORM: uniform_kernel,
        KernelType.EPANECHNIKOV: epanechnikov_kernel,
        KernelType.TRIANGULAR: triangular_kernel,
        KernelType.EPSILON: epsilon_kernel,
        KernelType.CUSTOM: custom_kernel_fn,
    }

    if kernel_type not in kernel_functions:
        raise ValueError(f"Unsupported kernel type: {kernel_type}")

    return kernel_functions[kernel_type]
