import operator
from functools import reduce
from typing import Any, Callable, List

import numpy as np
import torch
import torch.nn as nn

from .constants import MechanismFamily, NeuralNetworkType, NoiseMode, VariableDataType
from .variable import Variable


def _discretize_exogenous_variables(
    exogenous_vars: List[Variable],
):
    """
    Discretize each exogenous_var.value in exogenous_vars
    using exogenous_var.noise_regions (via np.digitize).
    """
    for noise_variable in exogenous_vars:
        # We assume noise_variable.noise_regions is set appropriately
        assert (
            noise_variable.noise_regions is not None
            and len(noise_variable.noise_regions) > 0
        ), "Discrete noise variables need regions"

        thresholds = np.array(noise_variable.noise_regions)

        noise_variable.value = np.digitize(
            noise_variable.value, thresholds, right=False
        )


def add_noise_to_mechanism(expression, exogenous_inputs, noise_mode):
    """
    Add noise to a given deterministic expression based on the noise mode.
    Given an expression (the deterministic part) from a structural equation
    include the exogenous inputs according to the noise_mode e.g. additive, multiplicative
    In the functional case, the exogenous inputs will be empty, they have already been included
    in the computation of the expression
    Handles multi-dimensional variables and batch processing.

    Args:
        expression: Deterministic part of the mechanism. Shape: (batch_size, output_dimensionality).
        exogenous_inputs: List of noise variables. Each noise variable's value has shape: (batch_size, noise_dimensionality).
        noise_mode: Noise mode (additive, multiplicative, or functional).

    Returns:
        Expression with noise applied. Shape: (batch_size, output_dimensionality).
    """
    # No noise to add
    if not exogenous_inputs:
        return expression

    # Functional noise is already incorporated in the expression
    if noise_mode == NoiseMode.FUNCTIONAL:
        return expression

    elif noise_mode == NoiseMode.ADDITIVE:
        # Sum noise contributions from all exogenous inputs
        total_noise = sum(noise.value for noise in exogenous_inputs)
        # Add noise to the expression
        return expression + total_noise

    elif noise_mode == NoiseMode.MULTIPLICATIVE:
        # Multiply noise contributions from all exogenous inputs
        total_noise = reduce(
            operator.mul,
            (noise.value for noise in exogenous_inputs),
            np.ones_like(expression),
        )
        # Multiply noise with the expression
        return expression * total_noise

    else:
        raise ValueError(f"Invalid noise mode {noise_mode}")


def create_linear_function(
    variable_dimensionality: int,
    parents: List[Variable],
    noise_mode: str,
    discrete_output=False,
):
    """
    Return a linear function that maps from the provided parent variables (to be concatenated)
    to a variable of dimensionality 'variable_dimensionality'.
    Noise is specified via the noise_mode variable.
    Args:
        variable_dimensionality: output variable dimensionality
        parents: List of input variables
        noise_mode: Mode of noise (additive, multiplicative, functional)
    """
    if noise_mode == NoiseMode.FUNCTIONAL:
        extra_inputs = []
        inputs = parents
    else:
        extra_inputs = [var for var in parents if var.exogenous]
        inputs = [var for var in parents if not var.exogenous]

    # Random weights and biases
    input_dim = sum(var.dimensionality for var in inputs)
    output_dim = variable_dimensionality
    weights = np.random.randn(input_dim, output_dim)  # Shape: (input_dim, output_dim)
    bias = np.random.randn(output_dim)  # Shape: (output_dim,)

    def linear_function():
        # Discretize exogenous variables if needed
        if discrete_output:
            _discretize_exogenous_variables(
                exogenous_vars=[parent for parent in parents if parent.exogenous]
            )

        if inputs:
            # Flatten and concatenate input values
            variable_values = [
                var.value.reshape(var.value.shape[0], -1) for var in inputs
            ]
            x = np.concatenate(
                variable_values, axis=1
            )  # Shape: (batch_size, input_dim)
            # Compute linear transformation
            linear_expression = x @ weights + bias  # Shape: (batch_size, output_dim)
        else:
            # No inputs; linear expression is just the bias broadcasted over the batch
            batch_size = extra_inputs[0].value.shape[0] if extra_inputs else 1
            linear_expression = np.tile(
                bias,
                (batch_size, 1),
                # np.zeros_like(bias), (batch_size, 1)
            )  # Shape: (batch_size, output_dim)
            # or one of np.zeros((batch_size, output_dim)) and np.ones((batch_size, output_dim)), as in:
            # linear_expression = 1 if noise_mode == NoiseMode.MULTIPLICATIVE else 0
        # Add noise according to noise mode
        return add_noise_to_mechanism(linear_expression, extra_inputs, noise_mode)

    return linear_function


def create_tabular_function(
    parents: List[Variable],
    mechanism_args: List[Any] = None,
    discrete_output=True,
    raise_on_no_match=True,
):
    """
    Create a tabular function (only for discrete variables).
    Supports parents with multi-dimensional values.

    Args:
        parents: List of parent variables whose values influence the output.
        mechanism_args: Specification of the tabular mapping. Each entry is a tuple:
                        [(List of input value tuples, output value)].
                        For example:
                        mechanism_args=[
                            ([(0, 0)], 1),  # Z = 1 when X = 0 and Y = 0
                            ([(0, 1), (1, 0)], 2),  # Z = 2 when (X, Y) is (0,1) or (1,0)
                        ]
        discrete_output (bool): Whether to discretize exogenous variables before processing.
        raise_on_no_match (bool): Whether to raise an error if no match is found.
    """
    if mechanism_args is None:
        raise ValueError("mechanism_args must be provided.")

    # Convert input combinations into a hashmap for fast lookup
    # Previous implementation used numpy broadcasting
    # Because of the size of the noise space, hashmaps are faster (comparisons are very slow otherwise).
    mechanism_dict = {
        tuple(pair): value for pairs, value in mechanism_args for pair in pairs
    }
    dimensionality = (
        1 if isinstance(mechanism_args[0][1], int) else len(mechanism_args[0][1])
    )

    def tabular_function():
        # Discretize exogenous variables if needed
        if discrete_output:
            _discretize_exogenous_variables(
                exogenous_vars=[p for p in parents if p.exogenous]
            )

        # Get values for all parent variables
        # Each p.value: (batch_size, var.dimensionality)
        variable_values = [p.value for p in parents]

        # Validate batch sizes
        batch_size = variable_values[0].shape[0]
        for v in variable_values:
            if v.shape[0] != batch_size:
                raise ValueError("All parent variables must have the same batch size.")

        # Flatten each variable's values along the feature dimension
        flattened_values = [v.reshape(batch_size, -1) for v in variable_values]

        # Concatenate flattened values along the feature axis
        inputs_array = np.concatenate(
            flattened_values, axis=1
        )  # Shape: (batch_size, total_dimensionality)
        # Convert to tuples for hashmap lookup
        input_tuples = [tuple(row) for row in inputs_array]

        MISSING = object()  # Unique sentinel value
        output = np.array([mechanism_dict.get(inp, MISSING) for inp in input_tuples])
        if raise_on_no_match and (MISSING in output):
            raise ValueError(
                f"Some inputs did not match any defined combinations. Unmatched: {np.array(input_tuples)[np.where(output == MISSING)[0]]}"
            )

        return output.reshape(-1, dimensionality)  # Shape: (batch_size, dimensionality)

    return tabular_function


def create_nn_function(
    variable_dimensionality: int,
    parents: List[Variable],
    noise_mode: str,
    mechanism_args: List[Any] = None,
    discrete_output=False,
):
    """
    Create a function modelled by a neural network.
    The mechanism_args specify the type of NN and layers.
    The first value specifies 'FF' or 'RNN', rest is dimensions of intermediate layers.
    """
    if mechanism_args is None or len(mechanism_args) < 1:
        raise ValueError(
            "Mechanism arguments must specify network type and layer dimensions"
        )

    # Input layer dimension is sum of dimensionalities of endogenous variables
    # The output layer dimension is equal to the variable's dimensionality
    network_type = mechanism_args[0]
    layer_dims = mechanism_args[1:]
    output_dim = variable_dimensionality

    if noise_mode == NoiseMode.FUNCTIONAL:
        extra_inputs = []
        inputs = parents
    else:
        extra_inputs = [var for var in parents if var.exogenous]
        inputs = [var for var in parents if not var.exogenous]

    input_dim = sum(var.dimensionality for var in inputs)
    layer_sizes = [input_dim] + layer_dims + [output_dim]

    # Handle case with no inputs (constant output based on bias)
    if input_dim == 0:

        def nn_function():
            batch_size = extra_inputs[0].value.shape[0] if extra_inputs else 1
            expression = (
                np.ones((batch_size, output_dim))
                if noise_mode == NoiseMode.MULTIPLICATIVE
                else np.zeros((batch_size, output_dim))
            )  # Default output
            return add_noise_to_mechanism(expression, extra_inputs, noise_mode)

        return nn_function

    # Define the neural network
    if network_type == NeuralNetworkType.FEEDFORWARD:

        class NeuralNet(nn.Module):
            def __init__(self, layer_sizes):
                super(NeuralNet, self).__init__()
                layers = []
                for i in range(len(layer_sizes) - 1):
                    layers.append(nn.Linear(layer_sizes[i], layer_sizes[i + 1]))
                    if i < len(layer_sizes) - 2:
                        layers.append(nn.ReLU())
                self.net = nn.Sequential(*layers)

            def forward(self, x):
                return self.net(x)

        nn_model = NeuralNet(layer_sizes)

        def nn_function():
            # Discretize exogenous variables if needed
            if discrete_output:
                _discretize_exogenous_variables(
                    exogenous_vars=[parent for parent in parents if parent.exogenous]
                )

            # Flatten and concatenate input values
            variable_values = [
                var.value.reshape(var.value.shape[0], -1) for var in inputs
            ]
            x = np.concatenate(
                variable_values, axis=1
            )  # Shape: (batch_size, input_dim)
            x_tensor = torch.tensor(x, dtype=torch.float32)  # Convert to PyTorch tensor
            with torch.no_grad():
                output_tensor = nn_model(x_tensor)  # Shape: (batch_size, output_dim)
            output = output_tensor.numpy()  # Convert back to numpy array
            # Add noise according to noise mode
            return add_noise_to_mechanism(output, extra_inputs, noise_mode)

        return nn_function

    else:
        raise NotImplementedError(f"Network type '{network_type}' is not implemented.")


def create_mechanism(
    variable: Variable,
    parents: List[Variable],
    mechanism_family: MechanismFamily,
    noise_mode: NoiseMode,
    mechanism_args: List[Any] = None,
    custom_function: Callable[[List[Variable]], Any] = None,
):
    """
    Create and return a function that serves as the mechanism for the passed variable.
    These functions don't need arguments. They are closures including all the values needed
    to compute the output of the mechanism using the latest values of the parents of the variable.
    Args:
        variable:
            Variable who's mechanism is created
        parents:
            Parent variables of the variable
        mechanism_family:
            What mechanism to be created
        noise_mode:
            How to incorporate noise into the mechanism e.g. additive, multiplicative, functional
        mechanism_args:
            Any arguments to the mechanism e.g. specification of the NN layers
        For more info check space_of_interest.py
    """
    if mechanism_family == MechanismFamily.LINEAR:
        return create_linear_function(
            variable.dimensionality,
            parents,
            noise_mode,
            discrete_output=variable.variable_type == VariableDataType.DISCRETE,
        )
    elif mechanism_family == MechanismFamily.NEURAL_NETWORK:
        return create_nn_function(
            variable.dimensionality,
            parents,
            noise_mode,
            mechanism_args,
            discrete_output=variable.variable_type == VariableDataType.DISCRETE,
        )
    elif mechanism_family == MechanismFamily.TABULAR:
        return create_tabular_function(
            parents,
            mechanism_args,
            discrete_output=variable.variable_type == VariableDataType.DISCRETE,
        )
    elif mechanism_family == MechanismFamily.CUSTOM:
        return lambda: custom_function(parents)
    else:
        raise ValueError(f"Unknown function family: {mechanism_family}")
