from typing import Any, Optional

import numpy as np

from .constants import VariableDataType, VariableRole


class Variable:
    def __init__(
        self,
        name: str,
        value: Optional[Any] = None,  # (batch_dimension, value_dimension)
        dimensionality: int = 1,
        exogenous: bool = False,
        variable_type: VariableDataType = VariableDataType.CONTINUOUS,
        num_discrete_values: int = None,
        variable_role: VariableRole = VariableRole.UNKNOWN,
        visible: bool = True,
    ):
        if not isinstance(name, str):
            raise TypeError("Variable name should be a string")
        if not isinstance(dimensionality, int):
            raise TypeError("Variable dimensionality should be an integer")

        self.name: str = name
        self.value: Optional[np.ndarray] = self._process_value(value, dimensionality)
        self.dimensionality: int = dimensionality
        self.exogenous = exogenous
        self.variable_type = variable_type
        self.variable_role = variable_role
        self.visible = visible
        if self.variable_type == VariableDataType.DISCRETE:
            assert num_discrete_values is not None
            self.num_discrete_values = num_discrete_values

    def _process_value(self, value: Any, dimensionality: int) -> Optional[np.ndarray]:
        """
        This function is useful for handling cases where the batch dimension in 1
        and don't want to bother adding extra dimensions before setting a variable's values
        """
        if value is None:
            return None

        # Convert integers to (1, 1) arrays
        if isinstance(value, (int, float)):
            value = np.array([[value]])

        # Convert 1D arrays to (1, value_dimension) arrays
        if isinstance(value, np.ndarray):
            if value.ndim == 1:
                value = value.reshape(1, -1)

        # Validate dimensionality
        if value.shape[-1] != dimensionality:
            raise ValueError(
                f"Provided value dimensionality {value.shape[-1]} does not match expected dimensionality {dimensionality}"
            )

        return value

    def set_value(self, new_value: Any):
        """Sets a new value for the variable, ensuring correct shape."""
        self.value = self._process_value(new_value, self.dimensionality)

    def set_role(self, new_role: VariableRole):
        """Sets a new role for the variable."""
        self.variable_role = new_role

    def set_visible(self, visible: bool):
        self.visible = visible

    def __repr__(self) -> str:
        return f"Variable(name={self.name}, value={self.value}, dimensionality={self.dimensionality}, exogenous={self.exogenous}, variable_type={self.variable_type})"

    def __str__(self) -> str:
        return self.name
