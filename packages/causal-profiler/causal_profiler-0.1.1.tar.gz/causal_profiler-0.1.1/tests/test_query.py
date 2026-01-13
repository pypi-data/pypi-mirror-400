import unittest

from causal_profiler.constants import QueryType, VariableDataType
from causal_profiler.query import Query
from causal_profiler.variable import Variable


class TestQuery(unittest.TestCase):
    def setUp(self):
        # Create variables for testing
        self.Y = [Variable(name="Y")]
        self.T = [Variable(name="T")]
        self.X = [Variable(name="X")]
        self.S = [Variable(name="S")]
        self.M = [Variable(name="M")]
        self.V_F = [Variable(name="V_F")]

    def test_conditional_query(self):
        """Test the string representation of a CONDITIONAL query"""
        query = Query.createL1Conditional(Y=self.Y, X=self.X, Y_value=5, X_value=1)
        expected_str = "P(Y=[5] | X=[1])"
        self.assertEqual(str(query), expected_str)

    def test_ate_query(self):
        """Test the string representation of an ATE query"""
        query = Query.createL2ATE(Y=self.Y, T=self.T, T1_value=1, T0_value=0)
        expected_str = "E[Y | do(T=[1])] - E[Y | do(T=[0])]"
        self.assertEqual(str(query), expected_str)

    def test_cate_query(self):
        """Test the string representation of a CATE query"""
        query = Query.createL2CATE(
            Y=self.Y, T=self.T, X=self.X, T1_value=1, T0_value=0, X_value=2
        )
        expected_str = "E[Y | do(T=[1]), X=[2]] - E[Y | do(T=[0]), X=[2]]"
        self.assertEqual(str(query), expected_str)

    def test_invalid_query_type(self):
        """Test invalid query type handling (if implemented in the future)"""
        with self.assertRaises(AssertionError):
            Query(query_type="INVALID", vars={}, vars_values={})

    def test_conditional_query_factory(self):
        """Test factory method for CONDITIONAL query"""
        query = Query.createL1Conditional(Y=self.Y, X=self.X, Y_value=5, X_value=1)
        self.assertEqual(query.type, QueryType.CONDITIONAL)
        self.assertIn("Y", query.vars)
        self.assertIn("X", query.vars)
        self.assertEqual(query.vars_values["Y"], [5])
        self.assertEqual(query.vars_values["X"], [1])

    def test_ate_query_factory(self):
        """Test factory method for ATE query"""
        query = Query.createL2ATE(Y=self.Y, T=self.T, T1_value=1, T0_value=0)
        self.assertEqual(query.type, QueryType.ATE)
        self.assertIn("Y", query.vars)
        self.assertIn("T", query.vars)
        self.assertEqual(query.vars_values["T"], ([1], [0]))

    def test_cate_query_factory(self):
        """Test factory method for CATE query"""
        query = Query.createL2CATE(
            Y=self.Y, T=self.T, X=self.X, T1_value=1, T0_value=0, X_value=2
        )
        self.assertEqual(query.type, QueryType.CATE)
        self.assertIn("Y", query.vars)
        self.assertIn("T", query.vars)
        self.assertIn("X", query.vars)
        self.assertEqual(query.vars_values["T"], ([1], [0]))
        self.assertEqual(query.vars_values["X"], [2])

    # TODO: to be added back when these queries are fixed
    # def test_L2ITE(self):
    #     query = Query.createL2ITE(Y=self.Y, T=self.T_with_value)
    #     self.assertEqual(query.type, QueryType.ITE)
    #     expected_str = "Y(T=1) - Y(T=0)"
    #     self.assertEqual(str(query), expected_str)

    # def test_L3CtfDE(self):
    #     query = Query.createL3CtfDE(Y=self.Y, S=self.S, M=self.M)
    #     self.assertEqual(query.type, QueryType.CTF_DE)
    #     expected_str = "[Y(M_S, S') - Y(M_S', S')]"
    #     self.assertEqual(str(query), expected_str)

    # def test_L3CtfIE(self):
    #     query = Query.createL3CtfIE(Y=self.Y, S=self.S, M=self.M)
    #     self.assertEqual(query.type, QueryType.CTF_IE)
    #     expected_str = "[Y(M_S', S) - Y(M_S', S')]"
    #     self.assertEqual(str(query), expected_str)

    def test_create_CtfTE_query(self):
        """
        Test creation of Ctf-TE query.
        """
        # Create variables
        Y = Variable(
            name="Y",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        T = Variable(
            name="T",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )
        V_F = [
            Variable(
                name="X1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="X2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        # Setup noise regions
        Y.noise_regions = [0.5]
        T.noise_regions = [0.5]
        V_F[0].noise_regions = [0.5]
        V_F[1].noise_regions = [0.5]

        # Create query
        query = Query.createL3CtfTE(
            Y=Y,
            T=T,
            V_F=V_F,
            T1_value=1,
            T0_value=0,
            V_F_value=[1, 0],
            Y_value=1,
        )

        # Check query representation
        expected_str = "P(Y=[1]_{do(T=[1])} | X1, X2=[1, 0]) - P(Y=[1]_{do(T=[0])} | X1, X2=[1, 0])"
        self.assertEqual(str(query), expected_str)

    def test_standard_form_CATE_query(self):
        # Create variables
        Y = [
            Variable(
                name="Y2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="Y1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        T = Variable(
            name="T2",
            variable_type=VariableDataType.DISCRETE,
            num_discrete_values=2,
        )

        X = [
            Variable(
                name="X2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="X3",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="X1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        # Setup noise regions
        Y[0].noise_regions = [0.5]
        Y[1].noise_regions = [0.5]
        T.noise_regions = [0.5]
        X[0].noise_regions = [0.5]
        X[1].noise_regions = [0.5]

        # Create query
        query1 = Query.createL2CATE(
            Y=Y,
            T=T,
            X=X,
            T1_value=6,
            T0_value=10,
            X_value=[5, 6, 4],
        )
        query2 = Query.createL2CATE(
            Y=Y[::-1],
            T=T,
            X=X[::-1],
            T1_value=6,
            T0_value=10,
            X_value=[5, 6, 4][::-1],
        )

        # Check query standard form
        self.assertEqual(query1.standard_form(), query2.standard_form())

    def test_standard_form_ATE_query(self):
        # Create variables
        Y = [
            Variable(
                name="Y2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="Y1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        T = [
            Variable(
                name="T2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="T1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="T3",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        # Setup noise regions
        Y[0].noise_regions = [0.5]
        Y[1].noise_regions = [0.5]
        T[0].noise_regions = [0.5]
        T[1].noise_regions = [0.5]

        # Create query
        query1 = Query.createL2ATE(
            Y=Y,
            T=T,
            T1_value=[1, 2, 6],
            T0_value=[3, 41, 1],
        )
        query2 = Query.createL2ATE(
            Y=Y[::-1],
            T=T[::-1],
            T1_value=[1, 2, 6][::-1],
            T0_value=[3, 41, 1][::-1],
        )

        # Check query standard form
        self.assertEqual(query1.standard_form(), query2.standard_form())

    def test_standard_form_CtfTE_query(self):
        # Create variables
        Y = [
            Variable(
                name="Y2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="Y1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        T = [
            Variable(
                name="T2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="T1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        V_F = [
            Variable(
                name="X2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="X1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        # Setup noise regions
        Y[0].noise_regions = [0.5]
        Y[1].noise_regions = [0.5]
        T[0].noise_regions = [0.5]
        T[1].noise_regions = [0.5]
        V_F[0].noise_regions = [0.5]
        V_F[1].noise_regions = [0.5]

        # Create query
        query1 = Query.createL3CtfTE(
            Y=Y,
            T=T,
            V_F=V_F,
            T1_value=[0, 1],
            T0_value=[2, 3],
            V_F_value=[4, 5],
            Y_value=[8, 9],
        )
        # reverse all arguments
        query2 = Query.createL3CtfTE(
            Y=Y[::-1],
            T=T[::-1],
            V_F=V_F[::-1],
            T1_value=[0, 1][::-1],
            T0_value=[2, 3][::-1],
            V_F_value=[4, 5][::-1],
            Y_value=[8, 9][::-1],
        )

        # Check query standard form
        self.assertEqual(query1.standard_form(), query2.standard_form())

    def test_multiple_variables_CtfTE_query(self):
        """
        Test that if there are multiple variables
        they are not sorted but their values are aligned.
        """
        # Create variables
        Y = [
            Variable(
                name="Y2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="Y1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        T = [
            Variable(
                name="T2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="T1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        V_F = [
            Variable(
                name="X2",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
            Variable(
                name="X1",
                variable_type=VariableDataType.DISCRETE,
                num_discrete_values=2,
            ),
        ]
        # Setup noise regions
        Y[0].noise_regions = [0.5]
        Y[1].noise_regions = [0.5]
        T[0].noise_regions = [0.5]
        T[1].noise_regions = [0.5]
        V_F[0].noise_regions = [0.5]
        V_F[1].noise_regions = [0.5]

        # Create query
        query = Query.createL3CtfTE(
            Y=Y,
            T=T,
            V_F=V_F,
            T1_value=[0, 1],
            T0_value=[2, 3],
            V_F_value=[4, 5],
            Y_value=[8, 9],
        )

        # Check query representation
        expected_str = "P(Y2, Y1=[8, 9]_{do(T2, T1=[0, 1])} | X2, X1=[4, 5]) - P(Y2, Y1=[8, 9]_{do(T2, T1=[2, 3])} | X2, X1=[4, 5])"
        expected_standard_form = (
            "QueryType.CTF_TE--T1=1--T2=0--T1=3--T2=2--X1=5--X2=4--Y1=9--Y2=8"
        )
        self.assertEqual(str(query), expected_str)
        self.assertEqual(query.standard_form(), expected_standard_form)

    def test_VariableStr(self):
        var = Variable(name="X")
        self.assertEqual(str(var), "X")
        var_with_value = Variable(name="X", value=5)
        self.assertEqual(str(var_with_value), "X")
        self.assertEqual(
            repr(var_with_value),
            "Variable(name=X, value=[[5]], dimensionality=1, exogenous=False, variable_type=VariableDataType.CONTINUOUS)",
        )

    def test_UnknownQueryType(self):
        with self.assertRaises(ValueError):
            Query(QueryType(99), {})  # Invalid query type

    def test_VarsAssignment(self):
        vars_dict = {"Y": self.Y, "T": self.T}
        query = Query(QueryType.CONDITIONAL, vars_dict)
        self.assertEqual(query.vars, vars_dict)

    def test_InvalidVariable(self):
        with self.assertRaises(TypeError):
            Variable(name=123)  # name should be a string

    def test_QueryTypeEnum(self):
        self.assertEqual(QueryType.CTF_TE.name, "CTF_TE")

    def test_CreateMethods(self):
        # Test that create methods return instances of Query
        query = Query.createL1Conditional(Y=self.Y, X=self.X, X_value=1, Y_value=0)
        self.assertIsInstance(query, Query)

    def test_QueryVarsContent(self):
        # Ensure that the vars dictionary contains correct keys and values
        query = Query.createL2CATE(
            Y=self.Y, T=self.T, X=self.X, X_value=0, T0_value=1, T1_value=2
        )
        self.assertIn("Y", query.vars)
        self.assertIn("T", query.vars)
        self.assertIn("X", query.vars)
        self.assertEqual(query.vars["Y"], self.Y)
        self.assertEqual(query.vars["T"], self.T)
        self.assertEqual(query.vars["X"], self.X)

    def test_get_target_info(self):
        """Test retrieving target variables."""
        query = Query.createL1Conditional(Y=self.Y, X=self.X, Y_value=5, X_value=1)
        self.assertEqual(query.get_target_info(), ("Y", self.Y))

    def test_get_intervened_info(self):
        """Test retrieving intervened variables."""
        query_ate = Query.createL2ATE(Y=self.Y, T=self.T, T1_value=1, T0_value=0)
        self.assertEqual(query_ate.get_intervened_info(), ("T", self.T))

        query_ctf_te = Query.createL3CtfTE(
            Y=self.Y,
            T=self.T,
            V_F=self.V_F,
            T1_value=1,
            T0_value=0,
            V_F_value=[0],
            Y_value=1,
        )
        self.assertEqual(query_ctf_te.get_intervened_info(), ("T", self.T))

        # CONDITIONAL query does not have intervened variables
        query_conditional = Query.createL1Conditional(
            Y=self.Y, X=self.X, Y_value=5, X_value=1
        )
        self.assertEqual(query_conditional.get_intervened_info(), (None, []))

    def test_get_conditioned_info(self):
        """Test retrieving conditioning variables."""
        query_conditional = Query.createL1Conditional(
            Y=self.Y, X=self.X, Y_value=5, X_value=1
        )
        self.assertEqual(query_conditional.get_conditioned_info(), ("X", self.X))

        query_cate = Query.createL2CATE(
            Y=self.Y, T=self.T, X=self.X, T1_value=1, T0_value=0, X_value=2
        )
        self.assertEqual(query_cate.get_conditioned_info(), ("X", self.X))

        query_ctf_te = Query.createL3CtfTE(
            Y=self.Y,
            T=self.T,
            V_F=self.V_F,
            T1_value=1,
            T0_value=0,
            V_F_value=[0],
            Y_value=1,
        )
        self.assertEqual(query_ctf_te.get_conditioned_info(), ("V_F", self.V_F))

        # ATE does not have conditioning variables
        query_ate = Query.createL2ATE(Y=self.Y, T=self.T, T1_value=1, T0_value=0)
        self.assertEqual(query_ate.get_conditioned_info(), (None, []))

    def test_outcome_interventional_prob_query(self):
        """Test the string representation of an Outcome Interventional Probability query"""
        query = Query.createL2OIP(
            Y=self.Y, T=self.T, X=self.X, Y_value=5, T_value=1, X_value=2
        )
        expected_str = "P(Y=[5] | do(T=[1]), X=[2])"
        self.assertEqual(str(query), expected_str)
        self.assertEqual(query.type, QueryType.OIP)
        self.assertIn("Y", query.vars)
        self.assertIn("T", query.vars)
        self.assertIn("X", query.vars)
        self.assertEqual(query.vars_values["Y"], [5])
        self.assertEqual(query.vars_values["T"], [1])
        self.assertEqual(query.vars_values["X"], [2])

    def test_get_info_methods_with_outcome_interventional_prob(self):
        """Test that get_conditioned_info and get_intervened_info work with OIP"""
        query = Query.createL2OIP(
            Y=self.Y, T=self.T, X=self.X, Y_value=5, T_value=1, X_value=2
        )
        self.assertEqual(query.get_conditioned_info(), ("X", self.X))
        self.assertEqual(query.get_intervened_info(), ("T", self.T))

    def test_outcome_interventional_prob_query_empty_conditioning(self):
        """Test OIP query with empty conditioning variables X=[]"""
        query = Query.createL2OIP(
            Y=self.Y, T=self.T, X=[], Y_value=5, T_value=1, X_value=[]
        )
        expected_str = "P(Y=[5] | do(T=[1]), =[])"
        self.assertEqual(str(query), expected_str)
        self.assertEqual(query.type, QueryType.OIP)
        self.assertIn("Y", query.vars)
        self.assertIn("T", query.vars)
        self.assertIn("X", query.vars)
        self.assertEqual(query.vars["X"], [])
        self.assertEqual(query.vars_values["Y"], [5])
        self.assertEqual(query.vars_values["T"], [1])
        self.assertEqual(query.vars_values["X"], [])

        # Test conditioning info with empty X
        self.assertEqual(query.get_conditioned_info(), ("X", []))
        self.assertEqual(query.get_intervened_info(), ("T", self.T))


if __name__ == "__main__":
    unittest.main()
