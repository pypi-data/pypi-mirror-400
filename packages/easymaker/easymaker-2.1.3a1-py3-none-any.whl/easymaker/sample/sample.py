import base64
from types import SimpleNamespace

import requests

from easymaker.common.codes import HyperparameterTypeCode, ModelFormatCode, ObjectiveTypeCode
from easymaker.common.parameter import Parameter
from easymaker.training.components import Dataset, HyperparameterSpec, Metric

training_iris = SimpleNamespace(
    pytorch=SimpleNamespace(
        image_name="Ubuntu 22.04 CPU PyTorch Training",
        source_dir_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-pytorch",
        entry_point="train_202403201459.py",
        nproc_per_node=1,
        use_torchrun=True,
        hyperparameter_list=[
            Parameter(parameter_name="epochs", parameter_value="10"),
            Parameter(parameter_name="batch_size", parameter_value="32"),
            Parameter(parameter_name="lr", parameter_value="0.01"),
        ],
        hyperparameter_spec_list=[
            HyperparameterSpec(
                hyperparameter_name="lr",
                hyperparameter_type_code=HyperparameterTypeCode.DOUBLE,
                hyperparameter_min_value="0.01",
                hyperparameter_max_value="0.05",
                hyperparameter_step="0.01",
            ),
            HyperparameterSpec(
                hyperparameter_name="batch_size",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="16",
                hyperparameter_max_value="32",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="epochs",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="10",
                hyperparameter_max_value="50",
                hyperparameter_step="1",
            ),
        ],
        metric_list=[
            Metric(name="Validation-accuracy"),
            Metric(name="Validation-loss"),
        ],
        metric_regex="([\w|-]+)\s*=\s*([+-]?\d*(\.\d+)?([Ee][+-]?\d+)?)",
        objective_metric_name="Validation-accuracy",
        objective_type_code=ObjectiveTypeCode.MAXIMIZE,
        objective_goal=0.999,
    ),
    tensorflow=SimpleNamespace(
        image_name="Ubuntu 22.04 CPU TensorFlow Training",
        source_dir_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-tensorflow",
        entry_point="train_20230906.0948.py",
        nproc_per_node=0,
        use_torchrun=False,
        hyperparameter_list=[
            Parameter(parameter_name="epochs", parameter_value="10"),
            Parameter(parameter_name="batch_size", parameter_value="32"),
            Parameter(parameter_name="learning_rate", parameter_value="0.01"),
        ],
        hyperparameter_spec_list=[
            HyperparameterSpec(
                hyperparameter_name="learning_rate",
                hyperparameter_type_code=HyperparameterTypeCode.DOUBLE,
                hyperparameter_min_value="0.01",
                hyperparameter_max_value="0.05",
                hyperparameter_step="0.01",
            ),
            HyperparameterSpec(
                hyperparameter_name="batch_size",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="16",
                hyperparameter_max_value="32",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="epochs",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="10",
                hyperparameter_max_value="50",
                hyperparameter_step="1",
            ),
        ],
        metric_list=[
            Metric(name="loss"),
            Metric(name="accuracy"),
            Metric(name="val_loss"),
            Metric(name="val_accuracy"),
        ],
        metric_regex="([\w|-]+)\s*:\s*([+-]?\d*(\.\d+)?([Ee][+-]?\d+)?)",
        objective_metric_name="val_loss",
        objective_type_code=ObjectiveTypeCode.MINIMIZE,
        objective_goal=0.00001,
    ),
    dataset_list=[
        Dataset(dataset_name="train", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-dataset/train"),
        Dataset(dataset_name="test", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-dataset/test"),
    ],
)

training_algorithm = SimpleNamespace(
    image_classification=SimpleNamespace(
        image_name="Image Classification CPU",
        algorithm_name="Image Classification",
        hyperparameter_list=[
            Parameter(parameter_name="input_size", parameter_value="28"),
            Parameter(parameter_name="learning_rate", parameter_value="0.01"),
            Parameter(parameter_name="logging_steps", parameter_value="500"),
            Parameter(parameter_name="num_train_epochs", parameter_value="2"),
            Parameter(parameter_name="per_device_eval_batch_size", parameter_value="16"),
            Parameter(parameter_name="per_device_train_batch_size", parameter_value="16"),
        ],
        dataset_list=[
            Dataset(dataset_name="train", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-algorithm-dataset/image-classification-minimize/train"),
            Dataset(dataset_name="validation", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-algorithm-dataset/image-classification-minimize/validation"),
        ],
        hyperparameter_spec_list=[
            HyperparameterSpec(
                hyperparameter_name="input_size",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="4",
                hyperparameter_max_value="28",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="learning_rate",
                hyperparameter_type_code=HyperparameterTypeCode.DOUBLE,
                hyperparameter_min_value="0.01",
                hyperparameter_max_value="0.05",
                hyperparameter_step="0.01",
            ),
            HyperparameterSpec(
                hyperparameter_name="logging_steps",
                hyperparameter_type_code=HyperparameterTypeCode.DISCRETE,
                hyperparameter_specified_values="500",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="num_train_epochs",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="1",
                hyperparameter_max_value="3",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="per_device_eval_batch_size",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="4",
                hyperparameter_max_value="16",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="per_device_train_batch_size",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="4",
                hyperparameter_max_value="16",
                hyperparameter_step="1",
            ),
        ],
        metric_list=[
            Metric(name="eval_loss"),
            Metric(name="eval_accuracy"),
            Metric(name="eval_precision"),
            Metric(name="eval_recall"),
            Metric(name="eval_f1"),
        ],
        metric_regex="'([\w|-]+)'\s*:\s*([+-]?\d*(\.\d+)?([Ee][+-]?\d+)?)",
        objective_metric_name="eval_loss",
        objective_type_code=ObjectiveTypeCode.MINIMIZE,
        objective_goal=0.00001,
    ),
    object_detection=SimpleNamespace(
        image_name="Object Detection CPU",
        algorithm_name="Object Detection",
        hyperparameter_list=[
            Parameter(parameter_name="learning_rate", parameter_value="0.0002"),
            Parameter(parameter_name="logging_steps", parameter_value="500"),
            Parameter(parameter_name="num_train_epochs", parameter_value="2"),
            Parameter(parameter_name="per_device_eval_batch_size", parameter_value="4"),
            Parameter(parameter_name="per_device_train_batch_size", parameter_value="4"),
        ],
        dataset_list=[
            Dataset(dataset_name="train", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-algorithm-dataset/object-detection/balloon_detection/train"),
            Dataset(dataset_name="test", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-algorithm-dataset/object-detection/balloon_detection/test"),
            Dataset(dataset_name="validation", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-algorithm-dataset/object-detection/balloon_detection/validation"),
        ],
        hyperparameter_spec_list=[
            HyperparameterSpec(
                hyperparameter_name="learning_rate",
                hyperparameter_type_code=HyperparameterTypeCode.DOUBLE,
                hyperparameter_min_value="0.0001",
                hyperparameter_max_value="0.0005",
                hyperparameter_step="0.0001",
            ),
            HyperparameterSpec(
                hyperparameter_name="logging_steps",
                hyperparameter_type_code=HyperparameterTypeCode.DISCRETE,
                hyperparameter_specified_values="500",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="num_train_epochs",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="1",
                hyperparameter_max_value="3",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="per_device_eval_batch_size",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="2",
                hyperparameter_max_value="4",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="per_device_train_batch_size",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="2",
                hyperparameter_max_value="4",
                hyperparameter_step="1",
            ),
        ],
        metric_list=[
            Metric(name="AP-IoU=0.50:0.95-area=all-maxDets=100"),
            Metric(name="AR-IoU=0.50:0.95-area=all-maxDets=100"),
        ],
        metric_regex="'([AP|AR]+-IoU=0.50:0.95-area=all-maxDets=100)':\\s([+-]?\\d*(\\.\\d+)?([Ee][+-]?\\d+)?)",
        objective_metric_name="AP-IoU=0.50:0.95-area=all-maxDets=100",
        objective_type_code=ObjectiveTypeCode.MAXIMIZE,
        objective_goal=0.999,
    ),
    semantic_segmentation=SimpleNamespace(
        image_name="Semantic Segmentation CPU",
        algorithm_name="Semantic Segmentation",
        hyperparameter_list=[
            Parameter(parameter_name="learning_rate", parameter_value="0.0002"),
            Parameter(parameter_name="logging_steps", parameter_value="500"),
            Parameter(parameter_name="num_train_epochs", parameter_value="2"),
            Parameter(parameter_name="per_device_train_batch_size", parameter_value="4"),
        ],
        dataset_list=[
            Dataset(dataset_name="train", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-algorithm-dataset/semantic-segmentation/train-minimize"),
            Dataset(dataset_name="test", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-algorithm-dataset/semantic-segmentation/test"),
            Dataset(dataset_name="validation", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-algorithm-dataset/semantic-segmentation/validation"),
            Dataset(dataset_name="resources", data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-algorithm-dataset/semantic-segmentation/resources"),
        ],
        hyperparameter_spec_list=[
            HyperparameterSpec(
                hyperparameter_name="learning_rate",
                hyperparameter_type_code=HyperparameterTypeCode.DOUBLE,
                hyperparameter_min_value="0.0001",
                hyperparameter_max_value="0.0005",
                hyperparameter_step="0.0001",
            ),
            HyperparameterSpec(
                hyperparameter_name="logging_steps",
                hyperparameter_type_code=HyperparameterTypeCode.DISCRETE,
                hyperparameter_specified_values="500",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="num_train_epochs",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="1",
                hyperparameter_max_value="3",
                hyperparameter_step="1",
            ),
            HyperparameterSpec(
                hyperparameter_name="per_device_train_batch_size",
                hyperparameter_type_code=HyperparameterTypeCode.INT,
                hyperparameter_min_value="2",
                hyperparameter_max_value="4",
                hyperparameter_step="1",
            ),
        ],
        metric_list=[
            Metric(name="eval_loss"),
            Metric(name="eval_mean_iou"),
            Metric(name="eval_mean_accuracy"),
            Metric(name="eval_overall_accuracy"),
        ],
        metric_regex="'(eval_loss|eval_mean_iou|eval_mean_accuracy|eval_overall_accuracy)'\s*:\s*([+-]?\d*(\.\d+)?([Ee][+-]?\d+)?)",
        objective_metric_name="eval_loss",
        objective_type_code=ObjectiveTypeCode.MINIMIZE,
        objective_goal=0.00001,
    ),
)


classification_model = SimpleNamespace(
    train=SimpleNamespace(
        source_dir_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-tensorflow",
        entry_point="train.py",
        dataset=SimpleNamespace(
            train="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-dataset/train",
            test="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-dataset/test",
        ),
    ),
    model_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-tensorflow-model",
    model_format=ModelFormatCode.TENSORFLOW,
    batch_inference=SimpleNamespace(
        input_data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-inference/case_4_1000_json",
        input_data_type="JSON",
    ),
    model_evaluation=SimpleNamespace(
        input_data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-dataset/model_evaluation",
        input_data_type="CSV",
        target_field_name="species",
        class_names="setosa,versicolor,virginica",
    ),
)

regression_model = SimpleNamespace(
    model_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/tabular-regression/model",
    model_format=ModelFormatCode.PYTORCH,
    model_evaluation=SimpleNamespace(
        input_data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/tabular-regression/data",
        input_data_type="CSV",
        target_field_name="quality",
    ),
)


# 인증 토큰 발급 가이드 : https://docs.nhncloud.com/ko/nhncloud/ko/public-api/api-authentication/#_1
def get_access_token(user_access_key_id, secret_access_key):
    credentials = f"{user_access_key_id}:{secret_access_key}"
    auth_header = f"Basic {base64.b64encode(credentials.encode('utf-8')).decode('utf-8')}"
    url = "https://oauth.api.nhncloudservice.com/oauth2/token/create"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": auth_header}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")


# TODO.가이드 노트북 다운로드
def download_guide_notebook():
    pass
