import os
import ssl

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.sessions import Session
from urllib3 import poolmanager

from easymaker.api.request_body import (
    BatchInferenceBody,
    EndpointCreateBody,
    ExperimentCreateBody,
    HyperparameterTuningCreateBody,
    ModelCreateBody,
    ModelEvaluationCreateBody,
    PipelineRecurringRunCreateBody,
    PipelineRunCreateBody,
    PipelineUploadBody,
    StageCreateBody,
    TrainingCreateBody,
)
from easymaker.common import constants, exceptions


class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        self.poolmanager = poolmanager.PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_context=ctx)


class ApiSender:
    def __init__(self, region, appkey, access_token=None, environment_type=None):
        self._environment_type = environment_type or os.environ.get("EM_ENVIRONMENT_TYPE", constants.DEFAULT_ENVIRONMENT_TYPE).lower()
        # 1. EM_API_URL 환경 변수가 있으면 해당 값 사용
        if os.environ.get("EM_API_URL"):
            self._easymakerApiUrl = os.environ.get("EM_API_URL")
        # 2. local 환경
        elif os.environ.get("EM_PROFILE", "").lower() == "local":
            self._easymakerApiUrl = "http://127.0.0.1:10090"
        # 3. 일반 환경 (alpha, beta, real)
        else:
            domain = constants.EASYMAKER_API_DOMAIN[self._environment_type]
            profile = os.environ.get("EM_PROFILE", "real").lower()
            # real 환경이면 빈 문자열, dev 환경이면 "-{profile}" 형태
            profile_suffix = "" if profile == "real" else f"-{profile}"
            self._easymakerApiUrl = constants.EASYMAKER_API_URL_TEMPLATE.format(region=region.lower(), profile=profile_suffix, domain=domain)

        self._easymakerApiUrl = self._easymakerApiUrl.rstrip("/")

        self._appkey = appkey
        self._access_token = access_token

        self.session = Session()
        self.session.mount("https://", TLSAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=Retry.RETRY_AFTER_STATUS_CODES)))
        self.session.headers.update(self._get_headers())

        if os.environ.get("EM_PROFILE", "").lower() not in ["local", "test"]:
            try:
                requests.get(self._easymakerApiUrl + "/nhn-api-gateway")
            except Exception:
                raise exceptions.EasyMakerRegionError("Invalid region")  # noqa B904

    @staticmethod
    def _is_successful(response):
        is_success = response["header"]["isSuccessful"]
        if not is_success:
            raise exceptions.EasyMakerError(response)

        return is_success

    def _get_client_ip(self):
        try:
            return self.session.get("http://127.0.0.1:8888/em_client_ip").json().get("client_ip")
        except Exception:
            return None

    def _get_headers(self):
        if os.environ.get("EM_TOKEN"):
            headers = {"X-EasyMaker-Token": os.environ.get("EM_TOKEN")}
        else:
            headers = {"x-nhn-authorization": f"Bearer {self._access_token}"}
        headers["Accept-Language"] = "en"
        em_client_ip = self._get_client_ip()
        if em_client_ip:
            headers["X-EasyMaker-Client-Ip"] = em_client_ip

        return headers

    def get_objectstorage_token(self, tenant_id=None, username=None, password=None):
        if os.environ.get("EM_TOKEN"):
            response = self.session.get(f"{self._easymakerApiUrl}/token/v1.0/appkeys/{self._appkey}/groups/{os.environ.get('EM_GROUP_ID')}/iaas-token").json()
            self._is_successful(response)
            return response
        else:
            if tenant_id and username and password:
                token_url = constants.OBJECT_STORAGE_TOKEN_URL[self._environment_type]
                req_header = {"Content-Type": "application/json"}
                body = {"auth": {"tenantId": tenant_id, "passwordCredentials": {"username": username, "password": password}}}
                response = self.session.post(token_url, headers=req_header, json=body).json()
                return response
            else:
                raise exceptions.EasyMakerError("Invalid object storage username/password")

    def get_instance_type_list(self, group_type=None, algorithm_id=None, model_id=None):
        params = {}
        if group_type:
            params["groupType"] = group_type
        if algorithm_id:
            params["algorithmId"] = algorithm_id
        if model_id:
            params["modelIdList"] = model_id
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/flavors", params=params).json()
        self._is_successful(response)
        return response["flavorList"]

    def get_image_list(self, group_type=None):
        params = {}
        if group_type:
            params["groupTypeCodeList"] = group_type
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/images", params=params).json()
        self._is_successful(response)

        return response["imageList"]

    def get_algorithm_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/algorithms").json()
        self._is_successful(response)

        return response["algorithmList"]

    def get_experiment_list(
        self,
        id_list: list[str] | None = None,
        name_list: list[str] | None = None,
    ) -> list[dict]:
        params = {}
        if id_list:
            params["experimentIdList"] = id_list
        if name_list:
            params["experimentNameList"] = name_list

        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/experiments", params=params).json()
        self._is_successful(response)

        return response["experimentList"]

    def create_experiment(self, body: ExperimentCreateBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/experiments",
            json=body.model_dump(),
        ).json()
        self._is_successful(response)

        return response["experiment"]

    def get_experiment_by_id(self, experiment_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/experiments/{experiment_id}").json()
        self._is_successful(response)

        return response["experiment"]

    def delete_experiment_by_id(self, experiment_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/experiments/{experiment_id}").json()
        self._is_successful(response)

        return response

    def run_training(self, body: TrainingCreateBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/trainings",
            json=body.model_dump(),
        ).json()

        self._is_successful(response)
        return response["training"]

    def get_training_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/trainings").json()
        self._is_successful(response)

        return response["trainingList"]

    def get_training_by_id(self, training_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/trainings/{training_id}").json()
        self._is_successful(response)

        return response["training"]

    def stop_training_by_id(self, training_id):
        response = self.session.put(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/trainings/{training_id}/stop").json()
        self._is_successful(response)

        return response

    def delete_training_by_id(self, training_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/trainings/{training_id}").json()
        self._is_successful(response)

        return response

    def run_hyperparameter_tuning(self, body: HyperparameterTuningCreateBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/hyperparameter-tunings",
            json=body.model_dump(),
        ).json()

        self._is_successful(response)
        return response["hyperparameterTuning"]

    def get_hyperparameter_tuning_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/hyperparameter-tunings").json()
        self._is_successful(response)

        return response["hyperparameterTuningList"]

    def get_hyperparameter_tuning_by_id(self, hyperparameter_tuning_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/hyperparameter-tunings/{hyperparameter_tuning_id}").json()
        self._is_successful(response)

        return response["hyperparameterTuning"]

    def stop_hyperparameter_tuning_by_id(self, hyperparameter_tuning_id):
        response = self.session.put(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/hyperparameter-tunings/{hyperparameter_tuning_id}/stop").json()
        self._is_successful(response)

        return response

    def delete_hyperparameter_tuning_by_id(self, hyperparameter_tuning_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/hyperparameter-tunings/{hyperparameter_tuning_id}").json()
        self._is_successful(response)

        return response

    def create_model(self, body: ModelCreateBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/models",
            json=body.model_dump(),
        ).json()
        self._is_successful(response)

        return response["model"]

    def get_model_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/models").json()
        self._is_successful(response)

        return response["modelList"]

    def get_model_by_id(self, model_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/models/{model_id}").json()
        self._is_successful(response)

        return response["model"]

    def delete_model_by_id(self, model_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/models/{model_id}").json()
        self._is_successful(response)

        return response

    def create_endpoint(self, body: EndpointCreateBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoints",
            json=body.model_dump(),
        ).json()
        self._is_successful(response)

        return response["endpoint"]

    def create_stage(self, body: StageCreateBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-stages",
            json=body.model_dump(),
        ).json()
        self._is_successful(response)

        return response["endpointStage"]

    def get_endpoint_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoints").json()
        self._is_successful(response)

        return response["endpointList"]

    def get_endpoint_by_id(self, endpoint_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoints/{endpoint_id}").json()
        self._is_successful(response)

        return response["endpoint"]

    def get_endpoint_stage_list(self, endpoint_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-stages", params={"endpointId": endpoint_id}).json()
        self._is_successful(response)

        return response["endpointStageList"]

    def get_endpoint_stage_by_id(self, endpoint_stage_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-stages/{endpoint_stage_id}").json()
        self._is_successful(response)

        return response["endpointStage"]

    def get_endpoint_model_list(self, endpoint_stage_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-models", params={"endpointStageId": endpoint_stage_id}).json()
        self._is_successful(response)

        return response["endpointModelList"]

    def get_endpoint_model_by_id(self, endpoint_model_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-models/{endpoint_model_id}").json()
        self._is_successful(response)

        return response["endpointModel"]

    def delete_endpoint_by_id(self, endpoint_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoints/{endpoint_id}").json()
        self._is_successful(response)

        return response

    def delete_endpoint_stage_by_id(self, endpoint_stage_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-stages/{endpoint_stage_id}").json()
        self._is_successful(response)

        return response

    def delete_endpoint_model_by_id(self, endpoint_model_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-models/{endpoint_model_id}").json()
        self._is_successful(response)

        return response

    def run_batch_inference(self, body: BatchInferenceBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/batch-inferences",
            json=body.model_dump(),
        ).json()

        self._is_successful(response)
        return response["batchInference"]

    def get_batch_inference_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/batch-inferences").json()
        self._is_successful(response)

        return response["batchInferenceList"]

    def get_batch_inference_by_id(self, batch_inference_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/batch-inferences/{batch_inference_id}").json()
        self._is_successful(response)

        return response["batchInference"]

    def stop_batch_inference_by_id(self, batch_inference_id):
        response = self.session.put(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/batch-inferences/{batch_inference_id}/stop").json()
        self._is_successful(response)

        return response

    def delete_batch_inference_by_id(self, batch_inference_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/batch-inferences/{batch_inference_id}").json()
        self._is_successful(response)

        return response

    def send_logncrash(self, logncrash_body):
        response = self.session.post(constants.LOGNCRASH_URL, json=logncrash_body).json()
        return response

    # Pipeline
    def upload_pipeline(self, body: PipelineUploadBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipelines/upload",
            json=body.model_dump(),  # camel case로 변환
        ).json()
        self._is_successful(response)

        return response["pipeline"]

    def get_pipeline_by_id(self, pipeline_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipelines/{pipeline_id}").json()
        self._is_successful(response)

        return response["pipeline"]

    def delete_pipeline_by_id(self, pipeline_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipelines/{pipeline_id}").json()
        self._is_successful(response)

        return response

    def get_pipeline_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipelines").json()
        self._is_successful(response)

        return response["pipelineList"]

    # Pipeline Run
    def get_pipeline_run_by_id(self, pipeline_run_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-runs/{pipeline_run_id}").json()
        self._is_successful(response)

        return response["pipelineRun"]

    def create_pipeline_run(self, body: PipelineRunCreateBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-runs",
            json=body.model_dump(),
        ).json()
        self._is_successful(response)

        return response["pipelineRun"]

    def stop_pipeline_run_by_id(self, pipeline_run_id):
        response = self.session.put(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-runs/{pipeline_run_id}/stop").json()
        self._is_successful(response)

        return response

    def delete_pipeline_run_by_id(self, pipeline_run_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-runs/{pipeline_run_id}").json()
        self._is_successful(response)

        return response

    def get_pipeline_run_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-runs").json()
        self._is_successful(response)

        return response["pipelineRunList"]

    # Pipeline Recurring Run
    def get_pipeline_recurring_run_by_id(self, pipeline_recurring_run_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-recurring-runs/{pipeline_recurring_run_id}").json()
        self._is_successful(response)

        return response["pipelineRecurringRun"]

    def create_pipeline_recurring_run(self, body: PipelineRecurringRunCreateBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-runs",
            json=body.model_dump(),
        ).json()
        self._is_successful(response)

        return response["pipelineRecurringRun"]

    def stop_pipeline_recurring_run_by_id(self, pipeline_recurring_run_id):
        response = self.session.put(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-recurring-runs/{pipeline_recurring_run_id}/stop").json()
        self._is_successful(response)

        return response

    def start_pipeline_recurring_run_by_id(self, pipeline_recurring_run_id):
        response = self.session.put(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-recurring-runs/{pipeline_recurring_run_id}/start").json()
        self._is_successful(response)

        return response

    def delete_pipeline_recurring_run_by_id(self, pipeline_recurring_run_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-recurring-runs/{pipeline_recurring_run_id}").json()
        self._is_successful(response)

        return response

    def get_pipeline_recurring_run_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/pipeline-recurring-runs").json()
        self._is_successful(response)

        return response["pipelineRecurringRunList"]

    # Model Evaluation
    def create_model_evaluation(self, body: ModelEvaluationCreateBody):
        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/model-evaluations",
            json=body.model_dump(),
        ).json()
        self._is_successful(response)

        return response["modelEvaluation"]

    def get_model_evaluation_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/model-evaluations").json()
        self._is_successful(response)

        return response["modelEvaluationList"]

    def get_model_evaluation_by_id(self, model_evaluation_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/model-evaluations/{model_evaluation_id}").json()
        self._is_successful(response)

        return response["modelEvaluation"]

    def stop_model_evaluation_by_id(self, model_evaluation_id):
        response = self.session.put(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/model-evaluations/{model_evaluation_id}/stop").json()
        self._is_successful(response)

        return response

    def delete_model_evaluation_by_id(self, model_evaluation_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/model-evaluations/{model_evaluation_id}").json()
        self._is_successful(response)

        return response
