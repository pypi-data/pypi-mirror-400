import json
import warnings


def warn_with_color(message, category, filename, lineno, file=None, line=None):
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    print(f"{YELLOW}{category.__name__}: {message}{RESET}")


warnings.showwarning = warn_with_color

from .constants import (
    EnumEncoder,
    FunctionSampling,
    KernelType,
    MechanismFamily,
    NoiseDistribution,
    NoiseMode,
    QueryType,
    VariableDataType,
)


class SpaceOfInterest:
    def __init__(
        self,
        # SCM space
        number_of_nodes=(5, 15),
        variable_dimensionality=(1, 1),
        mechanism_family=MechanismFamily.TABULAR,
        mechanism_args=None,
        expected_edges="N",
        number_of_categories=2,
        noise_mode=NoiseMode.ADDITIVE,  # has no effect in TABULAR mechanisms
        noise_distribution=NoiseDistribution.UNIFORM,
        number_of_noise_regions="V",
        noise_args=[-1, 1],
        variable_type=VariableDataType.CONTINUOUS,
        proportion_of_hidden_variables=0.0,
        discrete_function_sampling=FunctionSampling.SAMPLE_REJECTION,
        # Predefined graph
        predefined_graph_file=None,
        # Query Space
        number_of_queries=1,
        query_type=QueryType.CTF_TE,
        specific_query=None,
        allow_nan_queries=False,
        disable_query_sampling=False,
        ## Kernel weighting for continuous variables, ignored for DISCRETE variables
        kernel_type=KernelType.GAUSSIAN,
        kernel_bandwidth=0.1,
        kernel_fn=None,
        # Data space
        number_of_data_points=1000,
        **kwargs,
    ):
        """
        Create a space of interest.
        Check constants.py for all args that use an enum to check all possible values.
        Args:
            number_of_nodes:
                Range of the number of nodes in each graph
                e.g. [1, 10] for 1 to 10.
                To be sampled on each generated graph.
            variable_dimensionality:
                Range of the possible dimensionalities of the variables of the
                graphs of interest. Both numbers should be >= 1
                with the second one bigger than the first one.
            mechanism_family: (enum)
                Takes values in the MechanismFamily enum (constants.py)
                What type of function to have for mechanisms
                e.g. linear, neural network, tabular
            mechanism_args:
                Any arguments to pass to the mechanism specified in mechanism_family
                List of values e.g. ['FF', 4] for a FF NN with a single hidden layer of 4 neurons
                Breakdown of how these work:
                    - nn: first value specifies 'FF' or 'RNN', rest is dimensions of intermediate layers
                    - linear: unsupported
                    - tabular: Only provide this if you want ALL tabular functions to be exactly the same.
                        Otherwise leaving this empty will cause the sampler to sample random discrete functions.
                        List every single case as a List[Tuple[List[Tuple], Any]]
                        For example:
                        mechanism_args=[
                            ([(0, 0)], 1),  # Z = 1 when X = 0 and Y = 0
                            ([(0, 1), (1, 0)], 2),  # Z = 2 when (X, Y) is either (0, 1) or (1, 0)
                            ([(1, 1)], 1)   # Z = 1 when X = 1 and Y = 1
                        ]
            expected_edges:
                An expression that evaluates to the total expected number of edges.
                This field indirectly defines the edge probability.
                Numeric values, ranges and python expression are all accepted.
                e.g. (1, 5), 6, log(N) where N is the number of nodes and (x, y) is range
            number_of_categories:
                Only used when the variables are discrete. Specify a range of values for the number
                of categories of each discrete variable (also supports ints) e.g. (2, 3), (2, 2), 2
            noise_mode: (enum)
                How noise variables are incorporated in the structural equation
                e.g. additive, multiplicative, etc.
                This option is completely ignored if the mechanism_family is set to MechanismFamily.TABULAR
            noise_distribution: (enum)
                Distribution of noise variables e.g. Uniform
            number_of_noise_regions:
                Used to specify the number of noise regions in mechanisms
                This is an indicator of stochasticity/complexity. The more the
                number of noise regions, the more random / stochastic is the mechanism
                'V_to_PA' is a variable that can be used in any expression. it indicates
                |V|^Product(|PA(V)|) or \\Omega(V)^\\Omega(PA(V))
                N is the number of nodes, V is the number of values the variable takes
                number_of_noise_regions defaults to 'V'
                Examples:
                    1 - deterministic mechanism
                    3 - any positive integer
                    V - or any python expression
                    (1, N) - interval
                    V_to_PA/2
            noise_args:
                Arguments to the noise distribution
                e.g. [-1, 1] and Uniform give U(-1, 1)
            variable_type: (enum)
                Type of variables in the graph.
            proportion_of_hidden_variables:
                The proportion of the endogenous variables that will be hidden
                from the returned graph/queries/data.
                Must be a float in the range [0.0, 1.0], where:
                - `0.0` means no variables are hidden.
                - `1.0` means all endogenous variables are hidden.
                Defaults to 0.0.
            discrete_function_sampling: (enum)
                Method used for sampling discrete functions.
                Options are:
                - SAMPLE_REJECTION (default): Uses sample rejection algorithm.
                - ENUMERATE: Systematically enumerates all possibilities.
                - RANDOM: Uses random sampling.
            predefined_graph_file:
                Optional path to a YAML file containing a predefined graph structure.
                If provided, the graph will be loaded from this file instead of being sampled.
                The YAML file should have the following format:
                  edges:
                    - [X, Y]    # X -> Y
                    - [U, X]    # U -> X
                  node_attrs:   # Optional
                    U:
                      hidden: true
                When using a predefined graph, number_of_nodes and expected_edges are ignored.
                The full graph must be a valid DAG (no cycles).
                Defaults to None (graphs are sampled randomly).
            number_of_queries:
                Number of queries to be returned per sample, should be > 0
            query_type: (enum)
                Type of query to be returned e.g. Average Treatment Effect
            specific_query:
                String of a specific query of interest (see query.py)
            kernel_type: (enum)
                Type of kernel to use for kernel density estimation.
                If kernel_fn is provided, this will automatically be set to KernelType.CUSTOM.
            kernel_bandwidth:
                Bandwidth for the kernel density estimation
                Acts as epsilon threshold when using KernelType.EPSILON
            kernel_fn:
                Custom kernel function for weighting. If provided, automatically sets
                kernel_type to KernelType.CUSTOM. Should be a callable or None.
            number_of_data_points:
                Number of data points to return.
                These data points are used to answer causal queries.
                The value should be greater than 0.
            allow_nan_queries:
                Whether to allow queries that evaluate to NaN.
                If False (default), only queries with valid numeric estimates are returned.
                If True, queries that evaluate to NaN can also be included in the results.
            disable_query_sampling:
                Whether to disable query sampling and evaluation.
                This is useful for causal discovery tasks, and when enabled the queries are an empty list.
            **kwargs:
                Additional keyword arguments. If any unsupported fields are provided
                a warning will be issued and the fields will be ignored.
        """
        # Check for any unsupported fields and warn users
        if kwargs:
            unsupported_fields = list(kwargs.keys())
            field_list = ", ".join(f"'{field}'" for field in unsupported_fields)
            warning_msg = (
                f"The following fields are not supported in this version and will be ignored: "
                f"{field_list}. "
            )
            warnings.warn(warning_msg, UserWarning, stacklevel=2)

        # Validate predefined_graph_file
        assert isinstance(
            predefined_graph_file, (str, type(None))
        ), "predefined_graph_file must be a string path or None"

        # Validate
        def normalize_tuple_and_int_from_str(value):
            """
            Attempt to cast the input string to an int, or a tuple of the form '(a, b)', or leave it as a string.
            """
            if not isinstance(value, str):
                return value
            try:
                # Attempt to cast to int
                return int(value)

            except (ValueError, TypeError):
                # Attempt to cast to a tuple of the form '(a, b)'
                if value.startswith("(") and value.endswith(")"):
                    try:
                        stripped = value.strip("()")
                        a, b = map(int, stripped.split(","))
                        return (a, b)
                    except (ValueError, TypeError):
                        pass

            # If all parsing fails, return the original string
            return value

        assert (
            isinstance(number_of_nodes, tuple)
            and len(number_of_nodes) == 2
            and number_of_nodes[0] >= 1
            and number_of_nodes[1] >= 1
        ), "number_of_nodes must be a tuple with values >= 1"
        assert (
            isinstance(variable_dimensionality, tuple)
            and len(variable_dimensionality) == 2
            and all(x >= 1 for x in variable_dimensionality)
            and variable_dimensionality[1] >= variable_dimensionality[0]
        ), "variable_dimensionality must be a tuple of two numbers >= 1, with the second not smaller than the first"
        assert isinstance(
            mechanism_family, MechanismFamily
        ), f"mechanism_family must be in {MechanismFamily}"
        if mechanism_args is not None:
            assert isinstance(mechanism_args, list), "mechanism_args must be a list"
        expected_edges = normalize_tuple_and_int_from_str(expected_edges)
        # Accept lists of 2 elements
        if isinstance(expected_edges, list) and len(expected_edges) == 2:
            expected_edges = tuple(expected_edges)
        assert (
            expected_edges is not None
            and expected_edges != ""
            and isinstance(expected_edges, (str, tuple, int))
        ), "expected_edges must be a number, a range or a formula e.g. 2 or (5, 10) or log(N)"
        if isinstance(expected_edges, tuple):
            assert (
                expected_edges[0] <= expected_edges[1]
            ), "you need 'from <= to' when specifying a range for the total expected edges"
        number_of_categories = normalize_tuple_and_int_from_str(number_of_categories)
        assert isinstance(
            number_of_categories, (int, tuple)
        ), "number_of_categories must be a number or a range (tuple)"
        if isinstance(number_of_categories, tuple):
            assert (
                number_of_categories[0] <= number_of_categories[1]
            ), "you need 'from <= to' when specifying a range for the number of categories"
        assert isinstance(
            noise_mode, NoiseMode
        ), "noise_mode must be in one of ['functional', 'additive', 'multiplicative']"
        assert isinstance(
            noise_distribution, NoiseDistribution
        ), f"noise_distribution must be in {NoiseDistribution}"
        if not (
            isinstance(number_of_noise_regions, (str, tuple, int))
            or (
                number_of_noise_regions is None
                and variable_type == VariableDataType.CONTINUOUS
            )
        ):
            raise AssertionError(
                "number_of_noise_regions must be an int, an expression, a range (can include expression), "
                "or None if variable_type == CONTINUOUS"
            )
        if (
            isinstance(number_of_noise_regions, tuple)
            and isinstance(number_of_noise_regions[0], int)
            and isinstance(number_of_noise_regions[1], int)
        ):
            assert number_of_noise_regions[0] <= number_of_noise_regions[1]

        assert (
            isinstance(noise_args, list) and len(noise_args) == 2
        ), "noise_args must be a list of two elements"
        assert isinstance(
            variable_type, VariableDataType
        ), f"variable_type must be in {VariableDataType}"
        assert isinstance(
            proportion_of_hidden_variables, float
        ), "proportion_of_hidden_variables must be a float"

        assert (
            0.0 <= proportion_of_hidden_variables <= 1
        ), "proportion_of_hidden_variables must be a float in the range [0.0, 1.0]"
        assert isinstance(
            discrete_function_sampling, FunctionSampling
        ), f"discrete_function_sampling must be in {FunctionSampling}"
        assert number_of_queries > 0, "number_of_queries must be > 0"
        assert isinstance(query_type, QueryType), f"query_type must be in {QueryType}"
        assert isinstance(
            specific_query, (str, type(None))
        ), "specific_query must be a string or None"
        assert isinstance(
            kernel_type, KernelType
        ), f"kernel_type must be in {KernelType}"
        assert isinstance(
            kernel_bandwidth, (float, int)
        ), "kernel_bandwidth must be a float or int"
        assert kernel_fn is None or callable(
            kernel_fn
        ), "kernel_fn must be callable or None"
        assert number_of_data_points > 0, "number_of_data_points must be > 0"
        assert isinstance(
            allow_nan_queries, bool
        ), "allow_nan_queries must be a boolean"
        assert isinstance(
            disable_query_sampling, bool
        ), "disable_query_sampling must be a boolean"

        # If a custom kernel function is provided, set kernel_type to CUSTOM
        if kernel_fn is not None:
            kernel_type = KernelType.CUSTOM

        self.number_of_nodes = number_of_nodes
        self.variable_dimensionality = variable_dimensionality
        self.mechanism_family = mechanism_family
        self.mechanism_args = mechanism_args
        self.expected_edges = expected_edges
        self.predefined_graph_file = predefined_graph_file
        self.number_of_categories = (
            tuple(number_of_categories)
            if isinstance(number_of_categories, (tuple, list))
            else (number_of_categories, number_of_categories)
        )
        self.noise_distribution = noise_distribution
        # TODO: refactor when we allow for mixed SCMs
        self.number_of_noise_regions = (
            None
            if variable_type == VariableDataType.CONTINUOUS
            else number_of_noise_regions
        )
        self.noise_mode = noise_mode
        self.noise_args = noise_args
        self.variable_type = variable_type
        self.proportion_of_hidden_variables = proportion_of_hidden_variables
        self.discrete_function_sampling = discrete_function_sampling
        self.number_of_queries = number_of_queries
        self.query_type = query_type
        self.specific_query = specific_query
        self.allow_nan_queries = allow_nan_queries
        self.disable_query_sampling = disable_query_sampling
        self.number_of_data_points = number_of_data_points
        self.kernel_type = kernel_type
        self.kernel_bandwidth = kernel_bandwidth
        self.kernel_fn = kernel_fn

    def to_dict(self):
        """
        Return the Space of Interest in a dict format.
        """
        return {
            "number_of_nodes": self.number_of_nodes,
            "variable_dimensionality": self.variable_dimensionality,
            "mechanism_family": self.mechanism_family,
            "mechanism_args": self.mechanism_args,
            "expected_edges": self.expected_edges,
            "predefined_graph_file": self.predefined_graph_file,
            "number_of_categories": self.number_of_categories,
            "noise_distribution": self.noise_distribution,
            "number_of_noise_regions": self.number_of_noise_regions,
            "noise_mode": self.noise_mode,
            "noise_args": self.noise_args,
            "variable_type": self.variable_type,
            "proportion_of_hidden_variables": self.proportion_of_hidden_variables,
            "discrete_function_sampling": self.discrete_function_sampling,
            "number_of_queries": self.number_of_queries,
            "query_type": self.query_type,
            "specific_query": self.specific_query,
            "allow_nan_queries": self.allow_nan_queries,
            "disable_query_sampling": self.disable_query_sampling,
            "number_of_data_points": self.number_of_data_points,
            "kernel_type": self.kernel_type,
            "kernel_bandwidth": self.kernel_bandwidth,
            "kernel_fn": self.kernel_fn,
        }

    def save_to_file(self, filename):
        """
        Save the Space of Interest to a file.
        """

        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4, cls=EnumEncoder)

    @classmethod
    def load_from_file(cls, filename):
        def ensure_tuple_if_list(arg):
            """
            Convert input to a tuple if it is a list. Otherwise, return it unchanged.
            """
            return tuple(arg) if isinstance(arg, list) else arg

        """
        Load the Space of Interest from a file.
        """
        with open(filename, "r") as f:
            data = json.load(f)
        return cls(
            number_of_nodes=tuple(data["number_of_nodes"]),
            variable_dimensionality=tuple(data["variable_dimensionality"]),
            mechanism_family=MechanismFamily(data["mechanism_family"]),
            mechanism_args=data.get("mechanism_args"),
            expected_edges=ensure_tuple_if_list(data["expected_edges"]),
            predefined_graph_file=data.get("predefined_graph_file"),
            number_of_categories=ensure_tuple_if_list(data["number_of_categories"]),
            noise_distribution=NoiseDistribution(data["noise_distribution"]),
            number_of_noise_regions=ensure_tuple_if_list(
                data["number_of_noise_regions"]
            ),
            noise_mode=NoiseMode(data["noise_mode"]),
            noise_args=data["noise_args"],
            variable_type=VariableDataType(data["variable_type"]),
            proportion_of_hidden_variables=float(
                data["proportion_of_hidden_variables"]
            ),
            discrete_function_sampling=FunctionSampling(
                data.get(
                    "discrete_function_sampling",
                    FunctionSampling.SAMPLE_REJECTION.value,
                )
            ),
            number_of_queries=data["number_of_queries"],
            query_type=QueryType(data["query_type"]),
            specific_query=data.get("specific_query"),
            allow_nan_queries=data.get("allow_nan_queries", False),
            disable_query_sampling=data.get("disable_query_sampling", False),
            kernel_type=KernelType(data.get("kernel_type", KernelType.GAUSSIAN.value)),
            kernel_bandwidth=float(data.get("kernel_bandwidth", 0.1)),
            kernel_fn=data.get("kernel_fn"),
            number_of_data_points=data["number_of_data_points"],
        )

    def __str__(self):
        """
        Print the Space of Interest to the console.
        """
        return (
            f"SpaceOfInterest(\n"
            f"  number_of_nodes={self.number_of_nodes},\n"
            f"  variable_dimensionality={self.variable_dimensionality},\n"
            f"  mechanism_family='{self.mechanism_family}',\n"
            f"  mechanism_args={self.mechanism_args},\n"
            f"  expected_edges='{self.expected_edges}',\n"
            f"  predefined_graph_file='{self.predefined_graph_file}',\n"
            f"  number_of_categories:'{self.number_of_categories}',\n"
            f"  noise_mode='{self.noise_mode}',\n"
            f"  noise_distribution='{self.noise_distribution}',\n"
            f"  number_of_noise_regions='{self.number_of_noise_regions}',\n"
            f"  noise_args={self.noise_args},\n"
            f"  variable_type='{self.variable_type}',\n"
            f"  proportion_of_hidden_variables={self.proportion_of_hidden_variables},\n"
            f"  discrete_function_sampling='{self.discrete_function_sampling}',\n"
            f"  number_of_queries={self.number_of_queries},\n"
            f"  query_type='{self.query_type}',\n"
            f"  specific_query='{self.specific_query}',\n"
            f"  allow_nan_queries={self.allow_nan_queries},\n"
            f"  disable_query_sampling={self.disable_query_sampling},\n"
            f"  kernel_type='{self.kernel_type}',\n"
            f"  kernel_bandwidth={self.kernel_bandwidth},\n"
            f"  kernel_fn={self.kernel_fn},\n"
            f"  number_of_data_points={self.number_of_data_points},\n"
            f")"
        )

    def __eq__(self, other):
        """
        Compare whether two Spaces of Interest are equal.
        __eq__ enables the use of "==" between different instances
        of this class.
        """
        if not isinstance(other, SpaceOfInterest):
            return NotImplemented
        return (
            self.number_of_nodes == other.number_of_nodes
            and self.variable_dimensionality == other.variable_dimensionality
            and self.mechanism_family == other.mechanism_family
            and self.mechanism_args == other.mechanism_args
            and self.expected_edges == other.expected_edges
            and self.predefined_graph_file == other.predefined_graph_file
            and self.number_of_categories == other.number_of_categories
            and self.noise_mode == other.noise_mode
            and self.noise_distribution == other.noise_distribution
            and self.number_of_noise_regions == other.number_of_noise_regions
            and self.noise_args == other.noise_args
            and self.variable_type == other.variable_type
            and self.proportion_of_hidden_variables
            == other.proportion_of_hidden_variables
            and self.discrete_function_sampling == other.discrete_function_sampling
            and self.number_of_queries == other.number_of_queries
            and self.query_type == other.query_type
            and self.specific_query == other.specific_query
            and self.allow_nan_queries == other.allow_nan_queries
            and self.disable_query_sampling == other.disable_query_sampling
            and self.kernel_type == other.kernel_type
            and self.kernel_bandwidth == other.kernel_bandwidth
            and self.kernel_fn == other.kernel_fn
            and self.number_of_data_points == other.number_of_data_points
        )


if __name__ == "__main__":
    space = SpaceOfInterest()
    space.save_to_file("space_config.json")
    loaded_space = SpaceOfInterest.load_from_file("space_config.json")
    print(space)
    print(loaded_space)
    assert space == loaded_space
