from typing import Any, Dict, List, Tuple

from .constants import QueryType
from .utils import ensure_list
from .variable import Variable


class Query:
    """
    Represents a probabilistic or causal query, supporting various query types
    (e.g., conditional probabilities, causal effects, and counterfactuals).
    """

    def __init__(
        self,
        query_type: QueryType,
        vars: Dict[str, List[Variable]],
        vars_values: Dict[str, Any] = {},
    ):
        """
        Initializes a Query instance.

        Args:
            query_type (QueryType): The type of query (e.g., CONDITIONAL, ATE, CATE).
            vars (Dict[str, List[Variable]]):
                Mapping (dict) of variable labels (e.g., 'Y', 'X') to Variable objects.
                The labels are used to identify the different positions in each query.
                For the different queries see below. e.g. "T" is a label for treatment.
                vars_values: dictionary that maps any labels to set values.
                Any variable not set to any value won't have a key in this dict
                (e.g. Y in ATE - left side of an expectation).
                Counterfactuals aren't implemented yet but probably in that case the variable value
                will include the noise variable values.
                Note that the variable.value has nothing to do with the provided values.
                The variable.value will be reset once we sample once, the provided value
                is what we want to use in the query to estimate it.
            vars_values (Dict[str, Any]): Mapping of variable labels to their desired values.

        Raises:
            AssertionError: If query_type is not a valid QueryType.
        """
        assert isinstance(query_type, QueryType), f"Invalid query type {query_type}"
        self.type = query_type
        self.vars = vars
        self.vars_values = vars_values

    def get_conditioned_info(self) -> Tuple[str, List[Variable]]:
        """
        Returns:
            (conditioning_label, conditioning_vars):
                conditioning_label: str or None
                    The label in vars_values that corresponds to the conditioning variable(s)
                    (e.g. "X" for CONDITIONAL/CATE, "V_F" for CTF_TE)
                conditioning_vars: List[Variable]
                    The list of conditioning variables.

        If the query type does not have a conditioning variable (e.g. ATE), returns (None, []).
        """
        if self.type == QueryType.CONDITIONAL:
            return "X", self.vars.get("X", [])
        elif self.type == QueryType.CATE:
            return "X", self.vars.get("X", [])
        elif self.type == QueryType.CTF_TE:
            return "V_F", self.vars.get("V_F", [])
        elif self.type == QueryType.OIP:
            return "X", self.vars.get("X", [])
        else:
            return None, []

    def get_intervened_info(self) -> Tuple[str, List[Variable]]:
        """
        Retrieves intervened variable(s) and their label.

        Returns:
            Tuple[str, List[Variable]]:
                intervened_label: str or None
                    Label for the intervened variables (e.g., "T" for ATE, CATE, ITE).
                intervened_vars: List[Variable]
                    List of intervened variables.

        If no intervention exists, returns (None, []).
        """
        if self.type in {
            QueryType.ATE,
            QueryType.CATE,
            QueryType.ITE,
            QueryType.CTF_TE,
            QueryType.OIP,
        }:
            return "T", self.vars.get("T", [])
        return None, []

    def get_target_info(self) -> Tuple[str, List[Variable]]:
        """
        Retrieves the target variable(s) and their label.

        Returns:
            Tuple[str, List[Variable]]:
                target_label: str
                    Label for the target variable (always "Y").
                target_vars: List[Variable]
                    List of target variables being estimated.
        """
        return "Y", self.vars.get("Y", [])

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the query.

        Returns:
            str: Formatted query string.
        TODO: if variables have batch dimensions, printing won't be pretty this way
        """
        if self.type == QueryType.CONDITIONAL:
            # P(Y=y | X=x)
            Y_vars = ", ".join(str(v) for v in self.vars.get("Y", []))
            X_vars = ", ".join(str(v) for v in self.vars.get("X", []))
            Y_value = self.vars_values["Y"]
            X_value = self.vars_values["X"]
            return f"P({Y_vars}={Y_value} | {X_vars}={X_value})"
        elif self.type == QueryType.ATE:
            # E[Y | do(T=T1)] - E[Y | do(T=T0)]
            Y_vars = ", ".join(str(v) for v in self.vars.get("Y", []))
            T_vars = ", ".join(str(v) for v in self.vars.get("T", []))
            T_values = self.vars_values.get("T", [1, 0])
            return f"E[{Y_vars} | do({T_vars}={T_values[0]})] - E[{Y_vars} | do({T_vars}={T_values[1]})]"
        elif self.type == QueryType.CATE:
            # E[Y | do(T=T1), X] - E[Y | do(T=T0, X)]
            Y_vars = ", ".join(str(v) for v in self.vars.get("Y", []))
            T_vars = ", ".join(str(v) for v in self.vars.get("T", []))
            X_vars = ", ".join(str(v) for v in self.vars.get("X", []))
            T_values = self.vars_values.get("T", [1, 0])
            X_value = self.vars_values["X"]
            return f"E[{Y_vars} | do({T_vars}={T_values[0]}), {X_vars}={X_value}] - E[{Y_vars} | do({T_vars}={T_values[1]}), {X_vars}={X_value}]"
        elif self.type == QueryType.ITE:
            # TODO Y_i(T=1) - Y_i(T=0)
            Y_vars = ", ".join(str(v) for v in self.vars.get("Y", []))
            return f"{Y_vars}(T=1) - {Y_vars}(T=0)"
        elif self.type == QueryType.CTF_TE:
            Y_vars = ", ".join(str(v) for v in self.vars.get("Y", []))
            T_vars = ", ".join(str(v) for v in self.vars.get("T", []))
            V_F_vars = ", ".join(str(v) for v in self.vars.get("V_F", []))
            T_values = self.vars_values.get("T", [1, 0])
            V_F_value = self.vars_values["V_F"]
            Y_value = self.vars_values["Y"]
            return (
                f"P({Y_vars}={Y_value}_{{do({T_vars}={T_values[0]})}} | {V_F_vars}={V_F_value}) - "
                f"P({Y_vars}={Y_value}_{{do({T_vars}={T_values[1]})}} | {V_F_vars}={V_F_value})"
            )
        elif self.type == QueryType.OIP:
            Y_vars = ", ".join(str(v) for v in self.vars.get("Y", []))
            T_vars = ", ".join(str(v) for v in self.vars.get("T", []))
            X_vars = ", ".join(str(v) for v in self.vars.get("X", []))
            Y_value = self.vars_values["Y"]
            T_value = self.vars_values["T"]
            X_value = self.vars_values["X"]
            return f"P({Y_vars}={Y_value} | do({T_vars}={T_value}), {X_vars}={X_value})"
        elif self.type == QueryType.CTF_DE:
            # TODO
            # [Y(M_S, S') - Y(M_S', S')]_{S}
            Y_vars = ", ".join(str(v) for v in self.vars.get("Y", []))
            S_vars = ", ".join(str(v) for v in self.vars.get("S", []))
            M_vars = ", ".join(str(v) for v in self.vars.get("M", []))
            return f"[{Y_vars}(M_{S_vars}, S') - {Y_vars}(M_{S_vars}', S')]"
        elif self.type == QueryType.CTF_IE:
            # TODO
            # [Y(M_S', S) - Y(M_S', S')]_{S}
            Y_vars = ", ".join(str(v) for v in self.vars.get("Y", []))
            S_vars = ", ".join(str(v) for v in self.vars.get("S", []))
            M_vars = ", ".join(str(v) for v in self.vars.get("M", []))
            return f"[{Y_vars}(M_{S_vars}', S) - {Y_vars}(M_{S_vars}', S')]"
        else:
            return "Unknown Query Type"

    # Factory methods for creating queries
    @classmethod
    def createL1Conditional(
        cls, Y: List[Variable], X: List[Variable], Y_value: Any, X_value: Any
    ) -> "Query":
        Y, X, Y_value, X_value = ensure_list(Y, X, Y_value, X_value)
        vars: Dict[str, List[Variable]] = {"Y": Y, "X": X}
        vars_values: Dict[str, Any] = {"Y": Y_value, "X": X_value}
        return cls(QueryType.CONDITIONAL, vars, vars_values)

    @classmethod
    def createL2ATE(
        cls, Y: List[Variable], T: List[Variable], T1_value: Any, T0_value: Any
    ) -> "Query":
        Y, T, T1_value, T0_value = ensure_list(Y, T, T1_value, T0_value)
        vars: Dict[str, List[Variable]] = {"Y": Y, "T": T}
        vars_values: Dict[str, Any] = {"T": (T1_value, T0_value)}
        return cls(QueryType.ATE, vars, vars_values)

    @classmethod
    def createL2CATE(
        cls,
        Y: List[Variable],
        T: List[Variable],
        X: List[Variable],
        T1_value: Any,
        T0_value: Any,
        X_value: Any,
    ) -> "Query":
        Y, T, X, T1_value, T0_value, X_value = ensure_list(
            Y, T, X, T1_value, T0_value, X_value
        )
        vars: Dict[str, List[Variable]] = {"Y": Y, "T": T, "X": X}
        vars_values: Dict[str, Any] = {"T": (T1_value, T0_value), "X": X_value}
        return cls(QueryType.CATE, vars, vars_values)

    @classmethod
    def createL2OIP(
        cls,
        Y: List[Variable],
        T: List[Variable],
        X: List[Variable],
        Y_value: Any,
        T_value: Any,
        X_value: Any,
    ) -> "Query":
        """
        Creates a query to evaluate the outcome interventional probability P(Y=y | do(T=t), X=x).

        Args:
            Y: Target variables for which to compute probability.
            T: Variables to be intervened on.
            X: Conditioning variables.
            Y_value: The value for Y variables.
            T_value: The intervention value for T variables.
            X_value: The conditioning value for X variables.

        Returns:
            A Query object representing P(Y=y | do(T=t), X=x).
        """
        Y, T, X, Y_value, T_value, X_value = ensure_list(
            Y, T, X, Y_value, T_value, X_value
        )
        vars: Dict[str, List[Variable]] = {"Y": Y, "T": T, "X": X}
        vars_values: Dict[str, Any] = {"Y": Y_value, "T": T_value, "X": X_value}
        return cls(QueryType.OIP, vars, vars_values)

    @classmethod
    def createL2ITE(cls, Y: List[Variable], T: List[Variable]) -> "Query":
        Y, T = ensure_list(Y, T)
        vars: Dict[str, List[Variable]] = {"Y": Y, "T": T}
        return cls(QueryType.ITE, vars)

    @classmethod
    def createL3CtfDE(
        cls, Y: List[Variable], S: List[Variable], M: List[Variable]
    ) -> "Query":
        Y, S, M = ensure_list(Y, S, M)
        vars: Dict[str, List[Variable]] = {"Y": Y, "S": S, "M": M}
        return cls(QueryType.CTF_DE, vars)

    @classmethod
    def createL3CtfIE(
        cls, Y: List[Variable], S: List[Variable], M: List[Variable]
    ) -> "Query":
        Y, S, M = ensure_list(Y, S, M)
        vars: Dict[str, List[Variable]] = {"Y": Y, "S": S, "M": M}
        return cls(QueryType.CTF_IE, vars)

    @classmethod
    def createL3CtfSE(cls, Y: List[Variable], S: List[Variable]) -> "Query":
        Y, S = ensure_list(Y, S)
        vars: Dict[str, List[Variable]] = {"Y": Y, "S": S}
        return cls(QueryType.CTF_TE, vars)

    @classmethod
    def createL3CtfTE(
        cls,
        Y: List[Variable],
        T: List[Variable],
        V_F: List[Variable],
        T1_value: Any,
        T0_value: Any,
        V_F_value: List[Any],
        Y_value: Any,
    ) -> "Query":
        """
        Creates a Level 3 Counterfactual Total Effect (Ctf-TE) query.
        """
        Y, T, V_F, T1_value, T0_value, V_F_value, Y_value = ensure_list(
            Y, T, V_F, T1_value, T0_value, V_F_value, Y_value
        )
        vars: Dict[str, List[Variable]] = {"Y": Y, "T": T, "V_F": V_F}
        vars_values: Dict[str, Any] = {
            "T": (T1_value, T0_value),
            "V_F": V_F_value,
            "Y": Y_value,  # Target value of Y
        }
        return cls(QueryType.CTF_TE, vars, vars_values)

    def standard_form(self):
        """
        Returns a standard form string representation for checking uniqueness.
        """
        # TODO make T1_value and T0_value separate in the query representation
        # to avoid doing this
        standard_vars = self.vars.copy()
        standard_vars_values = self.vars_values.copy()
        if "T" in standard_vars:
            # For queries with treatment effects (ATE, CATE, CTF_TE), T values are tuples
            # For OIP queries, T values are single values
            if self.type in {QueryType.ATE, QueryType.CATE, QueryType.CTF_TE}:
                standard_vars["T0"] = standard_vars["T"]
                standard_vars["T1"] = standard_vars["T"]
                standard_vars.pop("T")
                standard_vars_values["T0"] = standard_vars_values["T"][0]
                standard_vars_values["T1"] = standard_vars_values["T"][1]
                standard_vars_values.pop("T")

        # TODO: write this more clearly
        sorted_items = sorted(
            (
                sorted(
                    zip(
                        [v.name for v in standard_vars[key]],  # Sort key
                        (
                            standard_vars_values[key]
                            if key in standard_vars_values
                            else ""
                        ),  # Maintain pairing
                    ),
                    key=lambda x: x[0],  # Sort by variable name (order within subgroup)
                )
                for key in standard_vars
            ),
            key=lambda x: (
                x[0][0] if x else ""
            ),  # Sort top-level by the first variable name if exists (order of subgroups)
        )

        variable_string = "--".join(
            f"{var}={value}" for key_vars in sorted_items for var, value in key_vars
        )

        return f"{self.type}--{variable_string}"


if __name__ == "__main__":
    Y = [Variable(name="Y")]
    X = [Variable(name="X")]

    query = Query.createL1Conditional(Y=Y, X=X)
    print(query)  # Outputs: P(Y | X)
