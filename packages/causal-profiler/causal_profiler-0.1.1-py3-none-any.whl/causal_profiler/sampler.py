import copy
import math
import random
from itertools import chain, product
from typing import Any, Dict, List, Set, Tuple, Union

import numpy as np

from .constants import FunctionSampling, MechanismFamily, QueryType, VariableDataType
from .query import Query
from .query_estimator import QueryEstimator
from .scm import SCM
from .space_of_interest import SpaceOfInterest
from .utils import load_graph_from_yaml
from .variable import Variable


class Sampler:
    def __init__(
        self,
        space_of_interest: SpaceOfInterest,
        return_adjacency_matrix: bool = False,
        n_samples=10000,
        max_query_attempts=100,  # Max number of times to retry sampling a query if the evaluation is NaN
    ):
        self.space_of_interest = space_of_interest
        self.n_samples = n_samples  # for queries evaluation
        self.query_estimator = QueryEstimator(
            self.n_samples,
            kernel_type=self.space_of_interest.kernel_type,
            kernel_bandwidth=self.space_of_interest.kernel_bandwidth,
            kernel_fn=self.space_of_interest.kernel_fn,
        )
        self.return_adjacency_matrix = return_adjacency_matrix
        self.max_query_attempts = max_query_attempts
        self.function_sampling = self.space_of_interest.discrete_function_sampling
        self.skip_trying_distinct_condition_values = True

    def _sample_number_of_nodes(self) -> int:
        """
        Sample the number of nodes from the specified range.
        """
        num_vars_min, num_vars_max = self.space_of_interest.number_of_nodes
        return random.randint(num_vars_min, num_vars_max)

    def _compute_edge_probability(self, N: int) -> float:
        """
        Compute the probability of an edge given the total expected edges and number of nodes N.
        expected_edges could be a number, a range, or an expression like "log(N)".
        For simplicity, we handle numeric or range. For expressions like 'log(N)',
        you might need an eval with a proper safe parser.
        """
        expected_edges = self.space_of_interest.expected_edges
        # Handle if expected_edges is a tuple range or a single number.
        if isinstance(expected_edges, tuple):
            # sample expected_edges from range
            expected_edges = random.uniform(expected_edges[0], expected_edges[1])
        elif isinstance(expected_edges, str):
            # Provide a safe namespace including common math functions and N
            safe_namespace = {"__builtins__": None, "N": N}
            safe_namespace.update(vars(math))  # Add all functions from the math module
            # e.g. expected_edges="log(N)+cos(N)"
            expected_edges = eval(expected_edges, safe_namespace)
        elif not isinstance(expected_edges, int):
            raise ValueError("expected_edges must be a numeric or recognized formula.")

        edge_probability = (
            2 * expected_edges / (N * (N - 1))
        )  # that divided by all the possible edges in a DAG
        # ensure the probability is between 0 and 1
        edge_probability = min(max(edge_probability, 0.0), 1.0)
        return edge_probability

    def _sample_dag(self, N: int, edge_probability: float) -> Dict[str, List[str]]:
        """
        Sample a DAG using the following algorithm:
        - Nodes: [X1, X2, ..., XN] with a causal order (1,...,N)
        - For i in [1..N]:
            number_parents_i ~ Binomial(i-1, edge_probability)
            Then sample parents from [X1,...,X_(i-1)].
        """
        node_names = [f"X{i}" for i in range(1, N + 1)]
        # adjacency list: node -> children
        graph = {node_name: [] for node_name in node_names}
        for i in range(1, N + 1):
            i_node = f"X{i}"
            possible_parents = [f"X{j}" for j in range(1, i)]
            if len(possible_parents) == 0:
                continue
            number_parents_i = np.random.binomial(
                len(possible_parents), edge_probability
            )
            if number_parents_i > 0:
                chosen_parents = random.sample(possible_parents, number_parents_i)
                # Add edges parent->child (parent->i_node)
                # We know this won't introduce a cycle by construction because parents < i_node
                for p in chosen_parents:
                    graph[p].append(i_node)
        return graph

    def _init_scm(
        self, graph: Dict[str, List[str]], hidden_nodes: Set[str] = None
    ) -> SCM:
        """
        Initialize the SCM with given parameters from the space of interest.

        Args:
            graph: Dictionary mapping parent nodes to children
            hidden_nodes: Optional set of node names that should be hidden
        """
        # Step 1: Create variables
        variables = self._create_variables(graph, hidden_nodes)

        # Step 2: Initialize the SCM object
        scm = SCM(
            variables=variables,
            noise_distribution=self.space_of_interest.noise_distribution,
            noise_mode=self.space_of_interest.noise_mode,
            noise_args=self.space_of_interest.noise_args,
            n_samples=self.space_of_interest.number_of_data_points,
        )

        # Step 3: Add edges to the SCM
        self._add_edges_to_scm(graph, scm, variables)

        # Step 4: Configure noise regions for exogenous variables
        # Sample the noise regions now that the graph is finalized
        self._configure_noise_regions(scm)

        # Step 5: Assign mechanisms to variables
        self._assign_mechanisms_to_variables(scm)

        return scm

    def _create_variables(
        self, graph: Dict[str, List[str]], hidden_nodes: Set[str] = None
    ) -> List[Variable]:
        """Create variables based on the graph structure.

        Args:
            graph: Dictionary mapping parent nodes to children
            hidden_nodes: Optional set of node names that should be hidden.
                         If None, uses proportion_of_hidden_variables to randomly select hidden nodes.
        """
        var_dim_min, var_dim_max = self.space_of_interest.variable_dimensionality
        # Sample variable dimensionality
        variable_dimensionality = random.randint(var_dim_min, var_dim_max)

        variables: List[Variable] = []
        for var_name in graph.keys():
            # Check if this node is specified as hidden in predefined graph
            is_hidden = hidden_nodes is not None and var_name in hidden_nodes

            var = Variable(
                name=var_name,
                dimensionality=variable_dimensionality,
                exogenous=False,  # For a Markovian SCM, typically internal vars are not exogenous
                variable_type=self.space_of_interest.variable_type,  # TODO: support for mixed SCMs
                num_discrete_values=(
                    random.randint(*self.space_of_interest.number_of_categories)
                    if self.space_of_interest.variable_type == VariableDataType.DISCRETE
                    else None
                ),
                visible=not is_hidden,  # Set visibility based on predefined hidden nodes
            )
            variables.append(var)

        # If no predefined hidden nodes, sample some variables to be set as unobserved
        if hidden_nodes is None:
            num_hidden_vars = int(
                self.space_of_interest.proportion_of_hidden_variables * len(variables)
            )
            hidden_vars = np.random.choice(
                variables, size=num_hidden_vars, replace=False
            )
            for var in hidden_vars:
                var.set_visible(False)
        return variables

    def _add_edges_to_scm(
        self, graph: Dict[str, List[str]], scm: SCM, variables: List[Variable]
    ):
        """Add edges to the SCM based on the graph structure."""
        # Input graph is parent->children
        var_dict = {v.name: v for v in variables}
        for parent_name, children in graph.items():
            for child_name in children:
                scm.add_edge(var_dict[parent_name], var_dict[child_name])

    def _configure_noise_regions(self, scm: SCM):
        """Configure noise regions for exogenous variables."""
        noise_expr = self.space_of_interest.number_of_noise_regions
        if noise_expr is None:
            return
        for var in scm.variables.values():
            if not var.exogenous:
                continue

            safe_namespace = {
                "__builtins__": None,
                "N": scm.count_endogenous_variables(),
                **vars(math),
            }
            noise_regions = self._compute_noise_regions(
                var, scm, noise_expr, safe_namespace
            )
            var.noise_regions = noise_regions
            var.num_discrete_values = len(noise_regions) + 1

    def eval_noise_expression(self, var, scm, expr, safe_namespace):
        """Evaluate the noise expression safely.
        TODO: var and scm probably shouldn't be arguments to this
        The best would be to pass clojures evaluating to V and V_to_PA
        """

        def compute_V_to_PA_value():
            """
            Compute the value of the 'V_to_PA' variable for the given exogenous var
            |V|^Product(|PA(V)|)
            """
            assert var.exogenous, "'V_to_PA' values exist only for exogenous variables"
            # Iterate over the children of the exogenous variable
            all_noise_regions = 1
            for child_id in scm.children.get(var.name, []):
                child_var = scm.variables[child_id]
                if child_var.variable_type == VariableDataType.DISCRETE:
                    all_noise_regions = max(
                        all_noise_regions,
                        child_var.num_discrete_values
                        ** np.prod(
                            [
                                parent.num_discrete_values
                                for parent in [
                                    scm.variables[parent_id]
                                    for parent_id in scm.parents[child_var.name]
                                ]
                                if not parent.exogenous
                            ]
                        ),
                    )

            return int(all_noise_regions)

        def compute_V_value():
            """
            Compute the value of V which is the maximum of the number of categories
            of any of the children of the exogenous variable in question
            """
            assert var.exogenous, "'V' values exist only for exogenous variables"
            maximum_V = 1
            for child_id in scm.children.get(var.name, []):
                child_var = scm.variables[child_id]
                if not child_var.exogenous:
                    maximum_V = max(maximum_V, child_var.num_discrete_values)
            return maximum_V

        try:
            # Try evaluating without 'V_to_PA' or 'V'
            noise_regions = eval(str(expr), safe_namespace)
        except Exception as e:
            # Add 'V' to the namespace and retry
            # V is the number of values the variable takes
            safe_namespace["V"] = compute_V_value()
            try:
                noise_regions = eval(str(expr), safe_namespace)
            except Exception as _:
                # Add 'V_to_PA' to the namespace and retry
                safe_namespace["V_to_PA"] = compute_V_to_PA_value()
                noise_regions = eval(str(expr), safe_namespace)
        return int(noise_regions)

    def _compute_noise_regions(self, var, scm, noise_expr, safe_namespace):
        """Compute the noise regions based on the given expression."""
        if isinstance(noise_expr, str):
            noise_regions_value = self.eval_noise_expression(
                var, scm, noise_expr, safe_namespace
            )
            noise_regions = np.sort(
                np.random.rand(int(noise_regions_value) - 1)
            ).tolist()
        elif isinstance(noise_expr, tuple):
            min_expr, max_expr = noise_expr
            min_val = self.eval_noise_expression(var, scm, min_expr, safe_namespace)
            max_val = self.eval_noise_expression(var, scm, max_expr, safe_namespace)
            noise_regions_value = random.randint(min_val, max_val)
            noise_regions = np.sort(np.random.rand(noise_regions_value - 1)).tolist()
        elif isinstance(noise_expr, int):
            noise_regions = np.sort(np.random.rand(noise_expr - 1)).tolist()
        else:
            assert False, f"Unsupported noise expression: {noise_expr}"

        return noise_regions

    def _assign_mechanisms_to_variables(self, scm: SCM):
        """Assign mechanisms to the variables in the SCM."""
        mechanism_family = self.space_of_interest.mechanism_family
        for var in scm.variables.values():
            if var.exogenous:
                continue
            mechanism_args = self.space_of_interest.mechanism_args
            if mechanism_args is None and mechanism_family == MechanismFamily.TABULAR:
                parent_vars = [
                    scm.variables[parent_id] for parent_id in scm.parents[var.name]
                ]
                mechanism_args = self.sample_discrete_function(
                    input_vars=parent_vars, output_var=var
                )
            scm.set_function(
                variable=var,
                mechanism_family=mechanism_family,
                mechanism_args=mechanism_args,
            )

    def _sample_single_value_for_vars(
        self, data: dict, *variables: Variable, same_datapoint: bool = True
    ):
        """
        Samples one value per variable from an SCM.

        Parameters:
            data: A dict from each variable name to a (M, N) np array where M is the number
                    of samples and N is the dimensionality of the variable
            *variables: Variable objects to sample.
             same_datapoint (bool, optional):
                    If True, all variables are sampled from the same data point (i.e., the same index in the data).
                    If False, each variable is sampled independently.


        Returns:
            list: List of sampled values, one per input variable.
        """
        sampled_values = []

        if same_datapoint:
            # Sample a single index from available data points
            index = np.random.randint(0, next(iter(data.values())).shape[0])

            for variable in variables:
                variable_data = data[variable.name]
                value = variable_data[index, :]
                if variable.variable_type == VariableDataType.CONTINUOUS:
                    # TODO: introduce r-balls
                    # raise NotImplemented("Continuous queries not supported yet")
                    pass
                sampled_values.append(value)

        else:
            for variable in variables:
                variable_data = data[variable.name]
                index = np.random.randint(0, variable_data.shape[0])
                value = variable_data[index, :]
                if variable.variable_type == VariableDataType.CONTINUOUS:
                    # TODO: introduce r-balls
                    # raise NotImplemented("Continuous queries not supported yet")
                    pass
                sampled_values.append(value)

        return sampled_values

    def _try_distinct_condition_values(
        self,
        scm: SCM,
        query: Query,
        data: dict,
        conditioning_label: str,
        conditioning_vars: List[Variable],
        fixed_values: Dict[str, Any],
        seen_queries: Set[str],
    ) -> float:
        """
        Try distinct values for the conditioning variable(s) when queries consistently return NaN.
        Pick a value for the conditioning variables that was already observed so that when you estimate the query it's certainly not None.

        Args:
            scm (SCM): The SCM object.
            query (Query): The query object.
            data (dict): The dataset of the variables from which to pick distinct values.
            conditioning_label (str): The label in query.vars_values that corresponds to conditioning variable.
            conditioning_vars (List[Variable]): The conditioning variables.
            fixed_values (Dict[str, Any]): The rest of the query's vars_values that should remain fixed.
            seen_queries (Set[str]): Previously evaluated queries.

        Returns:
            float: A non-NaN estimate if found, otherwise np.nan.
        """
        # Extract distinct candidate values for conditioning vars from data
        cond_data = {
            var.name: data[var.name] for var in conditioning_vars if var.name in data
        }
        # Create a list of tuples where each tuple contains the values for each variable
        conditioning_tuples = list(
            zip(*[cond_data[var.name] for var in conditioning_vars])
        )

        # Convert numpy arrays to tuples to make them hashable
        hashable_tuples = [
            tuple(map(tuple, conditioning_tuple))
            for conditioning_tuple in conditioning_tuples
        ]

        # Convert the list of tuples to a set to get unique tuples
        distinct_tuples = list(set(hashable_tuples))

        num_data_points = len(distinct_tuples)
        attempts = min(self.max_query_attempts, num_data_points)
        for i in range(attempts):
            new_query = copy.deepcopy(query)
            # Keep fixed values the same
            new_query.vars_values = copy.deepcopy(fixed_values)

            # Assign distinct values to corresponding conditioning variables
            new_query.vars_values[conditioning_label] = [
                np.array(value) for value in distinct_tuples[i]
            ]
            if new_query.standard_form() in seen_queries:
                continue

            estimate = self.query_estimator.evaluate_query(scm, new_query)
            # Check if estimate is valid based on allow_nan_queries setting
            estimate_is_valid = (
                not math.isnan(estimate) or self.space_of_interest.allow_nan_queries
            )
            if estimate_is_valid:
                return new_query, estimate
        return new_query, np.nan

    def _sample_and_evaluate_queries(self, scm: SCM) -> Tuple[List[Query], List[float]]:
        """
        Sample queries given the space_of_interest parameters.
        """
        queries = []
        estimates = []
        query_type = self.space_of_interest.query_type
        num_queries = self.space_of_interest.number_of_queries
        # These variables are used in the queries. They exclude hidden variables and exogenous variables.
        variables = [
            variable
            for variable in scm.variables.values()
            if not variable.exogenous and variable.visible
        ]

        # Sample a dataset of values.
        # From that dataset pick values for the queries from the domain of the variable as per the dataset.
        scm.reset_values(reset_noise=True)
        scm.sample_noise_variables()
        scm.compute_variables()
        data = {
            # You need np.copy because evaluating queries will modify this
            # since it's a reference to a single object that lives in the SCM
            var_id: np.copy(var.value)
            for var_id, var in scm.variables.items()
            if not var.exogenous and var.visible
        }

        seen_queries = set()

        for _ in range(num_queries):
            for _ in range(self.max_query_attempts):
                if query_type == QueryType.CONDITIONAL:
                    # conditional query: P(Y=y|X=x)
                    # pick Y and X
                    Y = random.choice(variables)
                    X = random.sample(
                        [v for v in variables if v != Y],
                        random.randint(1, len(variables) - 1),
                    )
                    Y_value = self._sample_single_value_for_vars(
                        data, Y, same_datapoint=False
                    )
                    X_value = self._sample_single_value_for_vars(data, *X)
                    new_query = Query.createL1Conditional(
                        Y=Y, X=X, Y_value=Y_value, X_value=X_value
                    )

                elif query_type == QueryType.OIP:
                    # OIP: P(Y=y | do(T=t), X=x)
                    Y = random.choice(variables)
                    T = random.choice([v for v in variables if v != Y])
                    # X can be empty (no conditioning) or a subset of remaining variables
                    remaining_vars = [v for v in variables if v not in [Y, T]]
                    if len(remaining_vars) > 0:
                        # Randomly decide whether to include conditioning variables
                        # Sample 0 to all remaining variables for conditioning
                        X = random.sample(
                            remaining_vars,
                            random.randint(0, len(remaining_vars)),
                        )
                    else:
                        X = []

                    Y_value = self._sample_single_value_for_vars(
                        data, Y, same_datapoint=False
                    )[0]
                    T_value = self._sample_single_value_for_vars(
                        data, T, same_datapoint=False
                    )[0]
                    X_value = (
                        self._sample_single_value_for_vars(data, *X)
                        if len(X) > 0
                        else []
                    )

                    new_query = Query.createL2OIP(
                        Y=Y, T=T, X=X, Y_value=Y_value, T_value=T_value, X_value=X_value
                    )
                elif query_type == QueryType.ATE:
                    # ATE: E[Y|do(T=1)] - E[Y|do(T=0)]
                    Y = random.choice(variables)
                    T = random.choice([v for v in variables if v != Y])
                    T1_value, T0_value = self._sample_single_value_for_vars(
                        data, T, T, same_datapoint=False
                    )
                    new_query = Query.createL2ATE(
                        Y=Y, T=T, T1_value=T1_value, T0_value=T0_value
                    )

                elif query_type == QueryType.CATE:
                    # CATE: E[Y|X=x, do(T=1)] - E[Y|X=x, do(T=0)]
                    Y = random.choice(variables)
                    T = random.choice([v for v in variables if v != Y])
                    X = random.sample(
                        [v for v in variables if v not in [Y, T]],
                        random.randint(1, len(variables) - 2),
                    )
                    T1_value, T0_value = self._sample_single_value_for_vars(
                        data, T, T, same_datapoint=False
                    )
                    X_value = self._sample_single_value_for_vars(data, *X)

                    new_query = Query.createL2CATE(
                        Y=Y,
                        T=T,
                        X=X,
                        T1_value=T1_value,
                        T0_value=T0_value,
                        X_value=X_value,
                    )

                elif query_type == QueryType.CTF_TE:
                    # Counterfactual TE: Need a V_F and Y-value, etc.
                    Y = random.choice(variables)
                    T = random.choice([v for v in variables if v != Y])
                    V_F = random.sample(
                        variables,
                        random.randint(
                            1, len(variables)
                        ),  # choose a random subset size
                    )
                    T1_value, T0_value, Y_value = self._sample_single_value_for_vars(
                        data, T, T, Y, same_datapoint=False
                    )
                    V_F_value = self._sample_single_value_for_vars(data, *V_F)
                    new_query = Query.createL3CtfTE(
                        Y=Y,
                        T=T,
                        V_F=V_F,
                        T1_value=T1_value,
                        T0_value=T0_value,
                        V_F_value=V_F_value,
                        Y_value=Y_value,
                    )
                else:
                    raise NotImplemented(f"{query_type} not supported!")

                query_standard_form = new_query.standard_form()
                if query_standard_form not in seen_queries:
                    estimate = self.query_estimator.evaluate_query(scm, new_query)
                    # Check if estimate is valid based on allow_nan_queries setting
                    estimate_is_valid = (
                        not math.isnan(estimate)
                        or self.space_of_interest.allow_nan_queries
                    )
                    if estimate_is_valid:
                        seen_queries.add(query_standard_form)
                        queries.append(copy.deepcopy(new_query))
                        estimates.append(estimate)
                        break
            else:
                # Getting here means we didn't manage to sample a unique and valid query
                # We'll try the fallback with the last "new_query" we tried to create (if it exists)
                if "new_query" not in locals():
                    # no query was attempted, just break
                    break
                cond_label = None
                cond_vars = []
                fixed_values = {}
                if query_type == QueryType.CONDITIONAL:
                    # conditioning on X
                    # TODO: refactor using query.get_conditioned_info
                    cond_label = "X"
                    fixed_values["Y"] = new_query.vars_values["Y"]
                    cond_vars = new_query.vars["X"]
                elif query_type == QueryType.CATE:
                    cond_label = "X"
                    fixed_values["T"] = new_query.vars_values["T"]
                    cond_vars = new_query.vars["X"]
                elif query_type == QueryType.CTF_TE:
                    cond_label = "V_F"
                    fixed_values["Y"] = new_query.vars_values["Y"]
                    fixed_values["T"] = new_query.vars_values["T"]
                    cond_vars = new_query.vars["V_F"]
                elif query_type == QueryType.OIP:
                    cond_label = "X"
                    fixed_values["Y"] = new_query.vars_values["Y"]
                    fixed_values["T"] = new_query.vars_values["T"]
                    cond_vars = new_query.vars["X"]
                if (
                    not self.skip_trying_distinct_condition_values
                    and cond_label is not None
                    and len(cond_vars) > 0
                ):
                    new_query, estimate = self._try_distinct_condition_values(
                        scm,
                        new_query,
                        data,
                        cond_label,
                        cond_vars,
                        fixed_values,
                        seen_queries,
                    )
                    query_standard_form = new_query.standard_form()
                    # Check if estimate is valid based on allow_nan_queries setting
                    estimate_is_valid = (
                        not math.isnan(estimate)
                        or self.space_of_interest.allow_nan_queries
                    )
                    if estimate_is_valid and not query_standard_form in seen_queries:
                        seen_queries.add(query_standard_form)
                        # TODO: this is deepcopied twice (also in _try_distinct_condition_values)
                        queries.append(copy.deepcopy(new_query))
                        estimates.append(estimate)
                # If estimate is invalid or duplicate, we skip this query and move on

        return (queries, estimates)

    def generate_scm(self) -> SCM:
        """
        Generates an SCM.
        If a predefined graph file is specified in space_of_interest, loads it.
        Otherwise, samples a random DAG.
        """
        # Check if we should use a predefined graph
        if self.space_of_interest.predefined_graph_file is not None:
            # Load predefined graph
            cg, hidden_nodes = load_graph_from_yaml(
                self.space_of_interest.predefined_graph_file
            )
            # Initialize SCM with predefined graph and hidden nodes
            scm = self._init_scm(cg, hidden_nodes)
        else:
            # 1. Sample number of nodes
            N = self._sample_number_of_nodes()
            # 2. Compute edge_probability
            edge_probability = self._compute_edge_probability(N)
            # 3. Sample causal graph (Markovian DAG)
            cg = self._sample_dag(N, edge_probability)
            # 4. Initialize SCM
            scm = self._init_scm(cg)

        scm.reset_values(reset_noise=True)
        return scm

    def generate_samples_and_queries(
        self,
    ) -> Tuple[
        Dict[str, np.ndarray],
        Tuple[List[Query], List[float]],
        Union[Dict[str, List[str]], np.ndarray],
    ]:
        """
        Generates an SCM and queries from the space_of_interest, samples data,
        evaluates queries, and returns (data, [(query, estimate), ...], graph).
        If a predefined graph file is specified in space_of_interest, loads it.
        Otherwise, samples a random DAG.
        """
        # Check if we should use a predefined graph
        if self.space_of_interest.predefined_graph_file is not None:
            # Load predefined graph
            cg, hidden_nodes = load_graph_from_yaml(
                self.space_of_interest.predefined_graph_file
            )
            # Initialize SCM with predefined graph and hidden nodes
            scm = self._init_scm(cg, hidden_nodes)
        else:
            # 1. Sample number of nodes
            N = self._sample_number_of_nodes()
            # 2. Compute edge_probability
            edge_probability = self._compute_edge_probability(N)
            # 3. Sample causal graph (Markovian DAG)
            cg = self._sample_dag(N, edge_probability)
            # 4. Initialize SCM
            scm = self._init_scm(cg)

        self._scm = scm  # for verification purposes
        # 5. Generate data
        scm.reset_values(reset_noise=True)
        scm.sample_noise_variables()
        scm.compute_variables()
        data = {
            var_id: var.value
            for var_id, var in scm.variables.items()
            if not var.exogenous and var.visible
        }

        # 6. Sample and evaluate queries (only if not disabled)
        if not self.space_of_interest.disable_query_sampling:
            (queries, estimates) = self._sample_and_evaluate_queries(scm)
        else:
            (queries, estimates) = ([], [])

        # 7. Return graph representation
        if self.return_adjacency_matrix:
            graph_repr = scm.extract_adjacency_matrix()
        else:
            graph_repr = scm.extract_adjacency_list()

        # Clean the values used to compute the queries so that the user doesn't see
        # the data used to compute the queries.
        for query in queries:
            for var in chain.from_iterable(query.vars.values()):
                var.value = None
        return data, (queries, estimates), graph_repr

    def sample_discrete_function(
        self, input_vars: List[Variable], output_var: Variable
    ):
        if self.function_sampling == FunctionSampling.ENUMERATE:
            return self.sample_discrete_function_enumerate(input_vars, output_var)
        elif self.function_sampling == FunctionSampling.RANDOM:
            return self.sample_discrete_function_random(input_vars, output_var)
        else:
            return self.sample_discrete_function_sample_rejection(
                input_vars, output_var
            )

    def sample_discrete_bijective_function(
        self, input_vars: List[Variable], output_var: Variable
    ) -> Dict[Tuple, List[Any]]:
        pass

    def sample_discrete_function_enumerate(
        self, input_vars: List[Variable], output_var: Variable
    ) -> Dict[Tuple, List[Any]]:
        """
        Samples a general discrete mechanism with the highest coverage for the output variable given input variables.

        Args:
            input_vars (List[Variable]): A list of parent variables (Pa(V)).
            output_var (Variable): The output variable (endogenous variable).

        Returns:
            Dict: A mechanism mapping parent configurations to output values based on exogenous noise regions.
        """

        # Step 1: Get the size of the output variable's domain
        # |\Omega(V)| = number of discrete values the output variable can take
        num_output_values = output_var.num_discrete_values

        # Step 2: Get the size of each input variable's domain
        # Generate the ranges of possible values for all parent variables (\Omega(PA(V)))
        # TODO: We disregard exogenous variables and assume they can be characterized by N_r
        # This isn't actually possible (at least not directly) when there are 2 noise variables on a single endogenous variable
        input_ranges = [
            range(var.num_discrete_values) for var in input_vars if not var.exogenous
        ]

        # Step 3: Calculate the total number of parent configurations
        # |\Omega(PA(V))| = the Cartesian product of all parent variable domains
        num_parent_combinations = int(np.prod([len(r) for r in input_ranges]))

        # Step 4: Calculate the total number of possible mappings
        # N_r = |\Omega(V)|^{|\Omega(PA(V))|}, the number of ways to map parent configs to output values
        N_r = num_output_values**num_parent_combinations
        # Noise regions shouldn't be more than the maximum
        if N_r < len(input_vars[0].noise_regions) + 1:
            new_noise_regions = np.sort(np.random.rand(N_r - 1)).tolist()
            input_vars[0].noise_regions = new_noise_regions
            input_vars[0].num_discrete_values = len(new_noise_regions) + 1

        # Step 5: Initialize a table to store all possible mappings
        # This table will enumerate every mapping from \Omega(PA(V)) to \Omega(V)
        mechanisms_table = []

        # u_lists tracks the regions of the exogenous noise U.
        # Initially, it contains the indices for all possible mappings (0 to N_r - 1).
        u_lists = [[i for i in range(N_r)]]

        # Step 6: Enumerate all parent configurations (\Omega(PA(V)))
        for pa_combination in product(
            *input_ranges
        ):  # Cartesian product of input variable domains
            new_u_lists = []  # Temporary storage for updated u_lists

            # Step 7: Iterate over the current list of mappings
            for u_list in u_lists:
                ind = 0  # Start index for dividing the current u_list

                # Step 8: For each possible output value (\Omega(V)), partition the current u_list
                for v in range(num_output_values):
                    # Divide u_list into equal-sized partitions for each output value
                    # Each partition corresponds to a subset of the possible mappings
                    new_u_list = u_list[ind : ind + len(u_list) // num_output_values]
                    ind += len(u_list) // num_output_values

                    # Append rows to mechanisms_table
                    # Each row specifies the parent combination, output value, and mapping index (1 mapping index = 1 noise region)
                    for u in new_u_list:
                        mechanisms_table.append([pa_combination, v, u])

                    # Store the partition for the next iteration
                    new_u_lists.append(new_u_list)

            # Update u_lists for the next parent configuration
            u_lists = new_u_lists

        # Step 9: Create the final mechanism dictionary
        mechanism = {}

        # Step 10: Populate the mechanism dictionary for each parent configuration
        for pa_combination in product(*input_ranges):  # Iterate over \Omega(PA(V))

            # Step 11: For each output value, find the noise regions corresponding to this mapping
            for v in range(num_output_values):
                region_indices = [
                    entry[2]  # Extract the noise region index
                    for entry in mechanisms_table
                    if entry[0] == pa_combination
                    and entry[1] == v  # Match parent configuration and output value
                ]
                for region in region_indices:
                    mechanism.setdefault(v, []).append((region,) + pa_combination)
                # TODO: The following way the region index maps to the |V| index
                # The mechanism maps parent configurations to lists of noise regions corresponding to output values
                # mechanism[pa_combination].append(region_indices)

        # Step 12: Return the final mechanism
        # Convert to the required "mechanism" format
        mechanism_list = [(inputs, output) for output, inputs in mechanism.items()]

        return mechanism_list

    def sample_discrete_function_sample_rejection(
        self, input_vars: List[Variable], output_var: Variable
    ) -> Dict[Tuple, List[Any]]:
        """
        Samples a general discrete mechanism with sample rejection.

        Args:
            input_vars (List[Variable]): A list of parent variables (Pa(V)).
            output_var (Variable): The output variable (endogenous variable).

        Returns:
            Dict: A mechanism mapping parent configurations to output values based on exogenous noise regions.
        """
        assert input_vars[
            0
        ].exogenous, "First variable of input vars should be exogenous."

        # Define the number of noise regions for the exogenous variable
        # Get the size of the output variable's domain
        num_output_values = output_var.num_discrete_values
        # Determine the ranges of possible values for all (non-exogenous) parent variables
        input_ranges = [
            range(var.num_discrete_values) for var in input_vars if not var.exogenous
        ]
        # Calculate the total number of parent configurations
        num_parent_combinations = np.prod([len(r) for r in input_ranges], dtype=object)
        # Calculate the number of ways to map parent configs to output values
        N_r_max = num_output_values**num_parent_combinations
        N_r = len(input_vars[0].noise_regions) + 1
        # Noise regions shouldn't be more than the maximum
        if N_r_max < N_r:
            if N_r_max == 0:
                print(
                    "Max number of noise regions is 0, this is invalid please check again the parameters of the space of interest or if this is an overflow"
                )
            N_r = N_r_max
            new_noise_regions = np.sort(np.random.rand(N_r - 1)).tolist()
            input_vars[0].noise_regions = new_noise_regions
            input_vars[0].num_discrete_values = len(new_noise_regions) + 1

        # Track seen output value mappings to ensure unique mechanisms
        seen_mapping = set()
        mechanism = {}

        for noise_region_id in range(N_r):
            # Placeholder for output values (ensures unique assignment later)
            output_values = None
            # Sample output values until a unique mapping is found
            while output_values is None or tuple(output_values) in seen_mapping:
                # Randomly assign output values for all parent combinations
                output_values = random.choices(
                    range(output_var.num_discrete_values), k=num_parent_combinations
                )
            seen_mapping.add(tuple(output_values))

            # Map each parent combination to its corresponding output value
            for pa_combination, output_value in zip(
                product(*input_ranges), output_values
            ):
                mechanism.setdefault(output_value, []).append(
                    (noise_region_id,) + pa_combination
                )

        # Convert the mechanism dictionary into the required format
        mechanism_list = [(inputs, output) for output, inputs in mechanism.items()]
        return mechanism_list

    def sample_discrete_function_random(
        self, input_vars: List[Variable], output_var: Variable
    ):
        """
        Samples an unbiased discrete function from input_vars to output_var.

        Args:
            input_vars (list): A list of Variable objects (input variables).
            output_var (Variable): A Variable object (output variable).

        Returns:
            list: A "mechanism" format definition of the function.
        """
        # Get the range of values for each input variable
        input_ranges = [
            product(range(var.num_discrete_values), repeat=var.dimensionality)
            for var in input_vars
        ]

        # Get the range of values for the output variable
        output_range = product(
            range(output_var.num_discrete_values), repeat=output_var.dimensionality
        )

        # Generate all possible input combinations
        input_combinations = list(product(*input_ranges))

        # Flatten the input combinations
        flattened_input_combinations = [
            tuple(chain.from_iterable(inp)) for inp in input_combinations
        ]

        # Randomly assign output values to input combinations
        random_output_assignments = random.choices(
            list(output_range), k=len(flattened_input_combinations)
        )

        # Group input combinations by their assigned output value
        mechanism = {}
        for inp, out in zip(flattened_input_combinations, random_output_assignments):
            mechanism.setdefault(out, []).append(inp)

        # Convert to the required "mechanism" format
        mechanism_list = [(inputs, output) for output, inputs in mechanism.items()]
        return mechanism_list
