from importlib import metadata

from easymaker import initializer
from easymaker.batch_inference import batch_inference
from easymaker.common import codes
from easymaker.common.parameter import Parameter
from easymaker.common.storage import Nas
from easymaker.endpoint import endpoint
from easymaker.endpoint.components import EndpointModelResource, ResourceOptionDetail
from easymaker.experiment import experiment
from easymaker.log import logger
from easymaker.model import model
from easymaker.model_evaluation import model_evaluation
from easymaker.pipeline import pipeline, pipeline_recurring_run, pipeline_run
from easymaker.storage import objectstorage
from easymaker.training import hyperparameter_tuning, training
from easymaker.training.components import Dataset, HyperparameterSpec, Metric

__version__ = metadata.version("easymaker")

easymaker_config = initializer.global_config

init = easymaker_config.init

logger = logger.Logger

Nas = Nas

Experiment = experiment.Experiment

Training = training.Training
Parameter = Parameter
Dataset = Dataset

HyperparameterTuning = hyperparameter_tuning.HyperparameterTuning
HyperparameterSpec = HyperparameterSpec
Metric = Metric

Model = model.Model
ModelFormatCode = codes.ModelFormatCode

Endpoint = endpoint.Endpoint
EndpointStage = endpoint.EndpointStage
EndpointModel = endpoint.EndpointModel
EndpointModelResource = EndpointModelResource
ResourceOptionDetail = ResourceOptionDetail

BatchInference = batch_inference.BatchInference

Pipeline = pipeline.Pipeline

PipelineRun = pipeline_run.PipelineRun

PipelineRecurringRun = pipeline_recurring_run.PipelineRecurringRun

ModelEvaluation = model_evaluation.ModelEvaluation

download = objectstorage.download

upload = objectstorage.upload

ObjectStorage = objectstorage.ObjectStorage


HyperparameterTypeCode = codes.HyperparameterTypeCode
ObjectiveTypeCode = codes.ObjectiveTypeCode
TuningStrategy = codes.TuningStrategy
EarlyStoppingAlgorithm = codes.EarlyStoppingAlgorithm
BatchInferenceInputDataTypeCode = codes.BatchInferenceInputDataTypeCode
ModelEvaluationInputDataTypeCode = codes.ModelEvaluationInputDataTypeCode
ScaleMetricCode = codes.ScaleMetricCode
ObjectiveCode = codes.ObjectiveCode

__all__ = (
    "init",
    "Training",
)
