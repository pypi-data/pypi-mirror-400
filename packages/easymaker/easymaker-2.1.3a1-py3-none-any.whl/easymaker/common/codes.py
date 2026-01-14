from enum import Enum


class ModelFormatCode(str, Enum):
    TENSORFLOW = "TENSORFLOW"
    PYTORCH = "PYTORCH"
    SCIKIT_LEARN = "SCIKIT_LEARN"
    HUGGING_FACE = "HUGGING_FACE"
    TENSORFLOW_TRITON = "TENSORFLOW_TRITON"
    PYTORCH_TRITON = "PYTORCH_TRITON"
    ONNX_TRITON = "ONNX_TRITON"


class HyperparameterTypeCode(str, Enum):
    INT = "int"
    DOUBLE = "double"
    DISCRETE = "discrete"
    CATEGORICAL = "categorical"


class ObjectiveTypeCode(str, Enum):
    MINIMIZE = "MINIMIZE"
    MAXIMIZE = "MAXIMIZE"


class TuningStrategy(str, Enum):
    GRID = "GRID"
    RANDOM = "RANDOM"
    BAYESIAN_OPTIMIZATION = "BAYESIAN_OPTIMIZATION"


class EarlyStoppingAlgorithm(str, Enum):
    MEDIAN = "MEDIAN"


class BatchInferenceInputDataTypeCode(str, Enum):
    JSON = "JSON"
    JSONL = "JSONL"


class ModelEvaluationInputDataTypeCode(str, Enum):
    JSONL = "JSONL"
    CSV = "CSV"


class ScaleMetricCode(str, Enum):
    CPU_UTILIZATION = "CPU_UTILIZATION"
    MEMORY_UTILIZATION = "MEMORY_UTILIZATION"


class ObjectiveCode(str, Enum):
    CLASSIFICATION = "CLASSIFICATION"
    REGRESSION = "REGRESSION"
