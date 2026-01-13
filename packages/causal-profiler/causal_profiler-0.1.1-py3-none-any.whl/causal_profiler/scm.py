from collections import deque
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .constants import (
    MechanismFamily,
    NoiseDistribution,
    NoiseMode,
    VariableDataType,
    VariableRole,
)
from .mechanism import create_mechanism
from .utils import broadcast_value_to_batch
from .variable import Variable


class SCM:
    def __init__(
        self,
        variables: List[Variable] = None,
        noise_distribution: str = NoiseDistribution.GAUSSIAN,
        noise_mode: NoiseMode = NoiseMode.ADDITIVE,
        noise_args: List[Any] = None,
        n_samples: int = 1,
    ):
        self.n_samples = n_samples  # to act as a batch-dimension for sampling
        self.noise_distribution = noise_distribution
        self.noise_mode = noise_mode
        self.noise_args = noise_args if noise_args is not None else []

        # Store variables in a dict from id to Variable
        self.variables: Dict[str, Variable] = {}
        # Parents and children map variable ID to lists of variable IDs
        self.parents: Dict[str, List[str]] = {}
        self.children: Dict[str, List[str]] = {}
        # From variable id to its function
        self.mechanisms: Dict[str, Any] = {}
        self.noise_variables: List[str] = []
        self.topological_sort_stale = True

        for var in variables or []:
            self.add_variable(var)

    def count_endogenous_variables(self):
        return len(self.variables) - len(self.noise_variables)

    def add_variable(self, variable: Variable):
        """
        Add a variable to the SCM. All non-exogenous variables immediately get an exogenous parent.

        Args:
            variable: The variable to add
        """
        self.topological_sort_stale = True
        var_id = variable.name
        self.variables[var_id] = variable
        self.parents[var_id] = []
        self.children[var_id] = []

        if not variable.exogenous:
            # Create an exogenous variable for this variable
            # Exogenous variables are always continuous, if discretization is needed
            # it happens in the mechanism (mechanism.py)
            noise_var = Variable(
                name=f"U_{variable.name}",
                dimensionality=variable.dimensionality,
                exogenous=True,
                variable_type=VariableDataType.CONTINUOUS,
                visible=False,
            )
            noise_var_id = noise_var.name
            self.variables[noise_var_id] = noise_var

            # Update the adjacency lists
            self.parents[var_id] = [noise_var_id]
            self.parents[noise_var_id] = []
            self.children[noise_var_id] = [var_id]
            self.children[var_id] = []
            self.noise_variables.append(noise_var_id)
        else:
            self.noise_variables.append(var_id)

    def add_edge(self, from_variable: Variable, to_variable: Variable):
        """
        Add a directed edge from one variable (from_variable) to another (to_variable)
        Both variables need to be part of the graph.
        It's possible that either variable is exogenous but it's not adviced to add an
        edge from an endogenous to an exogenous variable.

        Args:
            from_variable: variable where the edge starts from.
            to_variable: variable where the edges ends at.
        """
        self.topological_sort_stale = True
        from_id = from_variable.name
        to_id = to_variable.name

        # Assert that variables are part of this graph
        assert (
            from_id in self.parents and from_id in self.children
        ), f"{from_variable} isn't part of the SCM"
        assert (
            to_id in self.parents and to_id in self.children
        ), f"{to_variable} isn't part of the SCM"

        self.parents[to_id].append(from_id)
        self.children[from_id].append(to_id)

    def add_edges(self, edges: List[Tuple[Variable, Variable]]):
        """
        Add edges between a list of variables.

        Args:
            edges:
                List of pairs of variables.
                For each pair (a, b) the function adds a directed edge from a to b
        """
        for from_variable, to_variable in edges:
            self.add_edge(from_variable, to_variable)

    def set_function(
        self,
        variable: Variable,
        mechanism_family: MechanismFamily,
        mechanism_args: List[Any] = None,
        custom_function: Callable[[List[Variable]], Any] = None,
    ):
        """
        Set the mechanism that produces a variable that is already in the SCM.
        Provide the function family and the arguments of the mechanism.

        variable: the variable in question. All the variable's parents
            will be automatically read from the SCM
        mechanism_family: one of 'linear', 'nn', 'tabular'
        mechanism_args:
            - 'nn': first value specifies 'FF' or 'RNN', rest is dimensions of intermediate layers
            - 'linear': unsupported
            - 'tabular': List every single case as a List[Tuple[List[Tuple], Any]]
                For example:
                mechanism_args=[
                    ([(0, 0)], 1),  # Z = 1 when X = 0 and Y = 0
                    ([(0, 1), (1, 0)], 2),  # Z = 2 when (X, Y) is either (0, 1) or (1, 0)
                    ([(1, 1)], 1)   # Z = 1 when X = 1 and Y = 1
                ]
        """
        var_id = variable.name
        parent_vars = [self.variables[parent_id] for parent_id in self.parents[var_id]]

        self.mechanisms[var_id] = create_mechanism(
            variable=variable,
            parents=parent_vars,
            mechanism_family=mechanism_family,
            noise_mode=self.noise_mode,
            mechanism_args=mechanism_args,
            custom_function=custom_function,
        )

    def sample_variable(self, variable: Variable, n_samples: Optional[int] = None):
        n_samples = n_samples or self.n_samples
        if self.noise_distribution == NoiseDistribution.UNIFORM:
            # noise_args: [low, high]
            low, high = self.noise_args
            return np.random.uniform(
                low, high, size=(n_samples, variable.dimensionality)
            )
        elif self.noise_distribution == NoiseDistribution.GAUSSIAN:
            # noise_args: [mean, std]
            mean, std = self.noise_args
            return np.random.normal(
                mean, std, size=(n_samples, variable.dimensionality)
            )
        elif self.noise_distribution == NoiseDistribution.GAUSSIAN_MIXTURE:
            # noise_args: [mean1, std1, weight1, mean2, std2, weight2, ...]
            means = self.noise_args[::3]
            stds = self.noise_args[1::3]
            weights = self.noise_args[2::3]
            weights = np.array(weights)
            weights /= weights.sum()  # Normalize weights
            # Sample which component to use for each of the n_samples
            components = np.random.choice(len(weights), size=n_samples, p=weights)
            # Preallocate a noise array
            noise_values = np.empty((n_samples, variable.dimensionality))
            # Sample from the chosen components
            for i, component in enumerate(components):
                mean = means[component]
                std = stds[component]
                noise_values[i] = np.random.normal(
                    mean, std, size=variable.dimensionality
                )
            return noise_values
        else:
            raise ValueError(f"Unknown noise type: {self.noise_distribution}")

    def sample_noise_variable(self, noise_variable: Variable):
        """
        Sample value for the noise_variable provided.
        This has to be an exogenous variable.

        Args:
            noise_variable: The exogenous variable to be sampled.
        """
        assert (
            noise_variable.exogenous
        ), f"To sample a noise variable, it must be exogenous but {noise_variable} isn't"
        # Assign value to noise_variable.value based on self.noise_distribution and self.noise_args
        noise_variable.value = self.sample_variable(noise_variable)

    def sample_noise_variables(self):
        """
        Sample all noise (exogenous) variables of the SCM.
        To sample a new datapoint using the SCM one typically starts by sampling all
        the noise values (this function) and then propagating them with the mechanisms
        to the whole graph, by calling compute_variables
        """
        for noise_var_id in self.noise_variables:
            noise_var = self.variables[noise_var_id]
            self.sample_noise_variable(noise_var)

    def topological_sort(self) -> List[str]:
        in_degree = {var_id: len(parents) for var_id, parents in self.parents.items()}
        queue = deque([var_id for var_id, deg in in_degree.items() if deg == 0])
        sorted_vars = []

        while queue:
            var_id = queue.popleft()
            sorted_vars.append(var_id)
            for child_id in self.children.get(var_id, []):
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    queue.append(child_id)

        if len(sorted_vars) != len(self.variables):
            raise ValueError("The SCM graph has cycles.")
        return sorted_vars

    def compute_variable(self, variable: Variable, backwards: bool = False):
        """
        Compute the value of the provided variable for all samples in the batch.
        This is called after the ancestor (or all) exogenous variables have been sampled.
        The values are then propagated to compute the value of this variable.

        Args:
            variable: variable who's value is to be computed
            backwards: if true the function ensures that all parent variables are computed. This is by default False. If one needs to compute only a specific variable, they can set this to True.
        """
        var_id = variable.name
        if variable.value is not None:
            return  # Already computed or exogenous variable
        mechanism = self.mechanisms.get(var_id)
        if mechanism is None:
            raise ValueError(f"Function not set for variable {variable.name}")
        if backwards:
            # Ensure parent variables are computed
            for parent_id in self.parents[variable.name]:
                parent_var = self.variables[parent_id]
                if parent_var.value is None:
                    self.compute_variable(parent_var, backwards=backwards)
        variable.value = (
            mechanism()
        )  # Should return an array of shape (batch_size, dimensionality)
        return variable.value

    def do_hard_interventions(self, variables: List[Variable], values: List[Any]):
        """
        Applies hard interventions to the specified variables.
        """
        for variable, value in zip(variables, values):
            self.do_hard_intervention(variable, value)

    def do_hard_intervention(self, variable: Variable, value: Any):
        """
        Performs an intervention.
        The graph is recomputed only when a variable value isn't set,
        so setting a value is equivalent to an intervention (incoming edges have no
        effect because value won't be recomputed).

        Args:
            variable:
                Variable to be intervened.
            value:
                Value to set the variable to. Can be a pre-broadcasted array
                or a scalar/1D array to be broadcasted.
        """
        if isinstance(value, np.ndarray) and value.ndim == 2:
            # Validate shape of pre-broadcasted array
            if value.shape != (self.n_samples, variable.dimensionality):
                raise ValueError(
                    f"Provided value shape {value.shape} does not match "
                    f"expected shape ({self.n_samples}, {variable.dimensionality})"
                )
            broadcasted_value = value
        else:
            # Broadcast scalar or 1D array
            broadcasted_value = broadcast_value_to_batch(value, self.n_samples)

        variable.set_value(broadcasted_value)
        variable.variable_role = VariableRole.INTERVENED

    def remove_interventions(self, variables: List[Variable]):
        for variable in variables:
            self.remove_intervention(variable)

    def remove_intervention(self, variable: Variable):
        variable.variable_role = VariableRole.UNKNOWN

    def compute_variables(self):
        """
        Compute the values of all variables. This is usually called after all the noise
        variables have been sampled with sample_noise_variables. This function then
        propagates their values to the entire SCM using the mechanisms and computes the
        values of all variables.
        """
        # Forward compute all variables in SCM, assume sample_noise_variables was called
        if self.topological_sort_stale:
            self.sorted_vars = self.topological_sort()
            self.topological_sort_stale = False
        for var_id in self.sorted_vars:
            var = self.variables[var_id]
            self.compute_variable(var)

    def reset_values(self, reset_noise=True):
        """
        Clean the value of all variables of the SCM.
        Resetting the values also nullifies interventions.

        Args:
            reset_noise:
                Whether to reset noise variables or not. This is useful if one
                needs to regenerate data with the same noise e.g. in a counterfactual
                or when needing to evaluate 2 interventions with the same noise
                (as in the average treatment effect).
        """
        for variable in self.variables.values():
            if (
                reset_noise or not variable.exogenous
            ) and not variable.variable_role == VariableRole.INTERVENED:
                variable.value = None

    def sample_data(self, total_samples: int, batch_size: int = None):
        """
        Samples total_samples samples using the causal graph.
        This is done in batches of size batch_size.
        This defaults to n_samples that is provided on initialization of the SCM.
        The caller has the freedom to change the batch dimension of the variables
        in the SCM.
        For now the total_samples HAVE TO BE DIVISIBLE by batch_size.

        Args:
            total_samples:
                Total number of samples to return
            batch_size:
                Batch size of the final dataset. Defaults to n_samples which was provided on init to the SCM.
        """
        if batch_size is None:
            batch_size = self.n_samples

        data = {var_id: [] for var_id in self.variables.keys()}
        for start in range(0, total_samples, batch_size):
            end = min(start + batch_size, total_samples)
            self.n_samples = end - start
            self.reset_values()
            self.sample_noise_variables()
            self.compute_variables()
            # Collect values
            for var_id, var in self.variables.items():
                data[var_id].append(var.value)
        # Concatenate batches
        for var_id in data:
            data[var_id] = np.concatenate(data[var_id], axis=0)
        return data

    def extract_adjacency_list(self):
        """
        Extract adjacency list from SCM graph to be given to the user.
        Non-visible variables (hidden endogenous or exogenous) are projected out,
        introducing directed edges between their visible parents and children and
        bidirectional edges between all visible descendants of non-visible variables.
        """
        if self.topological_sort_stale:
            self.sorted_vars = self.topological_sort()
            self.topological_sort_stale = False

        # Mapping of variable names to unique indices (visible only)
        var_to_idx = {
            var_id: idx
            for idx, var_id in enumerate(
                var_id for var_id in self.sorted_vars if self.variables[var_id].visible
            )
        }

        # Initialize adjacency dictionary for visible variables
        adjacency_dict = {idx: [] for idx in var_to_idx.values()}

        def find_visible_parents(variable: Variable, visible_parents_indices: set):
            """
            Recursively finds all visible parent variables of the given variable.

            :param variable: The current variable being processed.
            :param visible_parents: Set to store visible parents of the initial variable.
            """
            for parent_name in self.parents[variable.name]:
                parent = self.variables[parent_name]
                if parent.visible:
                    # If the parent is visible, add it to the set
                    visible_parents_indices.add(var_to_idx[parent_name])
                else:
                    # If the parent is hidden, continue exploring its parents
                    find_visible_parents(parent, visible_parents_indices)

        def find_visible_children(variable: Variable, visible_children_indices: set):
            """
            Recursively finds all visible child variables of the given variable.

            :param variable: The current variable being processed.
            :param visible_children: Set to store visible children of the initial variable.
            """
            for child_name in self.children[variable.name]:
                child = self.variables[child_name]
                if child.visible:
                    # If the child is visible, add it to the set
                    visible_children_indices.add(var_to_idx[child_name])
                else:
                    # If the child is hidden, continue exploring its children
                    find_visible_children(child, visible_children_indices)

        # TODO: this and find_visible_children are equivalent!
        # Recursive function to find all visible descendants of a hidden variable
        def find_visible_descendants(variable):
            """
            Recursively find all visible descendants of a given variable.

            :param variable: The variable to start the search from.
            :return: A set of visible descendant variables.
            """
            descendants = set()
            for child in self.children[variable]:
                if self.variables[child].visible:
                    descendants.add(child)
                else:
                    descendants.update(find_visible_descendants(child))
            return descendants

        # Process all variables
        for var in self.sorted_vars:
            if self.variables[var].visible:
                # Add edges for visible variables
                for child in self.children[var]:
                    if self.variables[child].visible:
                        adjacency_dict[var_to_idx[var]].append(var_to_idx[child])
            else:
                # Handle non-visible variables with recursive propagation
                visible_parents_indices, visible_children_indices = set(), set()
                find_visible_parents(self.variables[var], visible_parents_indices)
                find_visible_children(self.variables[var], visible_children_indices)
                # Add edges between all visible parents and visible children
                for parent in visible_parents_indices:
                    for child in visible_children_indices:
                        adjacency_dict[parent].append(child)

                # Add bidirectional edges between all visible descendants
                visible_descendants = list(find_visible_descendants(var))
                for i, desc_a in enumerate(visible_descendants):
                    for j, desc_b in enumerate(visible_descendants):
                        if i != j:
                            adjacency_dict[var_to_idx[desc_a]].append(
                                var_to_idx[desc_b]
                            )

        # Remove duplicate edges in the adjacency dictionary
        for parent, child_list in adjacency_dict.items():
            adjacency_dict[parent] = list(set(child_list))

        # Return sorted list of visible variables
        visible_sorted_vars = [
            var_id for var_id in self.sorted_vars if self.variables[var_id].visible
        ]
        return adjacency_dict, visible_sorted_vars

    def extract_adjacency_matrix(self):
        """
        Extract adjacency matrix from SCM graph. This represents the graph
        with a binary matrix where matrix[i][j] = 1 indicates a directed edge
        from node i to node j.

        :return: adjacency_matrix (2D list), idx_to_variable_id (list of variable names)
        """
        # Extract adjacency list and variable ordering
        adjacency_list, idx_to_variable_id = self.extract_adjacency_list()
        num_variables = len(idx_to_variable_id)

        # Initialize an empty adjacency matrix
        adjacency_matrix = [[0] * num_variables for _ in range(num_variables)]

        # Fill the adjacency matrix based on the adjacency list
        for parent, children in adjacency_list.items():
            for child in children:
                adjacency_matrix[parent][child] = 1

        return adjacency_matrix, idx_to_variable_id
