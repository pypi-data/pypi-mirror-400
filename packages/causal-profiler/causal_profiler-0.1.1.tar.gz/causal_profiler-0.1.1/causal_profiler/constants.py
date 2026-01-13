import json
from enum import Enum

##### UTILS #####


class EnumUtilities(Enum):
    """
    Mixin that allows to list the values of the enum
    """

    @classmethod
    def list_values(cls):
        return [member.value for member in cls]


class EnumEncoder(json.JSONEncoder):
    """
    Serialize enums manually because they aren't
    supported by json
    """

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


##### ENUMS #####


class FunctionSampling(EnumUtilities):
    SAMPLE_REJECTION = "sample-rejection"
    ENUMERATE = "enumerate"
    RANDOM = "random"


class NoiseMode(EnumUtilities):
    ADDITIVE = "additive"
    MULTIPLICATIVE = "multiplicative"
    FUNCTIONAL = "functional"


class MechanismFamily(EnumUtilities):
    LINEAR = "linear"
    NEURAL_NETWORK = "nn"
    TABULAR = "tabular"
    CUSTOM = "custom"  # provide your own python function


class NeuralNetworkType(EnumUtilities):
    # TODO: only FF is supported now
    FEEDFORWARD = "FF"
    CNN = "CNN"
    RNN = "RNN"
    TRANSFORMER = "transformer"


class NoiseDistribution(EnumUtilities):
    UNIFORM = "uniform"
    GAUSSIAN = "gaussian"
    GAUSSIAN_MIXTURE = "gaussian-mixture"


class VariableDataType(EnumUtilities):
    CONTINUOUS = "continuous"
    DISCRETE = "discrete"


class QueryType(EnumUtilities):
    # Level 1
    CONDITIONAL = "conditional"
    # Level 2
    CATE = "CATE"
    ATE = "ATE"
    ITE = "ITE"
    DTE = "DTE"
    CDTE = "CDTE"
    OIP = "outcome_interventional_probability"
    # Level 3
    CTF_DE = "Ctf-DE"
    CTF_IE = "Ctf-IE"
    CTF_TE = "Ctf-TE"


class VariableRole(EnumUtilities):
    # TODO: if not used remove, set it when intervened for example
    UNKNOWN = "unknown"
    OBSERVED = "observed"
    INTERVENED = "intervened"
    CONDITIONED = "conditioned"


class ErrorMetric(EnumUtilities):
    L1 = "L1"
    L2 = "L2"
    HAMMING = "hamming"
    COSINE = "cosine"
    MSE = "MSE"
    MAPE = "MAPE"


class KernelType(EnumUtilities):
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    EPANECHNIKOV = "epanechnikov"
    TRIANGULAR = "triangular"
    EPSILON = "epsilon"
    CUSTOM = "custom"
