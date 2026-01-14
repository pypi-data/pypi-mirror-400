from typing import Any

from pydantic import ConfigDict, Field

import easymaker
from easymaker.api.request_body import ModelCreateBody
from easymaker.common.base_model.easymaker_base_model import EasyMakerBaseModel
from easymaker.common.codes import ModelFormatCode


class Model(EasyMakerBaseModel):
    model_id: str | None = None
    model_name: str | None = None  # TODO. model_name이 BaseModel 예약어라 충돌이나는데 어떻게 처리할지 확인 필요
    model_status_code: str | None = None
    training: Any | None = None
    hyperparameter_tuning: Any | None = None
    framework_version: str | None = None
    model_format_code: ModelFormatCode | None = Field(default=None, alias="modelTypeCode")
    model_upload_uri: str | None = None

    def create(
        self,
        model_name: str,
        model_format_code: ModelFormatCode,
        model_upload_uri: str | None = None,
        training_id: str | None = None,
        hyperparameter_tuning_id: str | None = None,
        description: str | None = None,
        parameter_list: list[Any] | None = None,
        wait: bool | None = True,
    ):
        response = easymaker.easymaker_config.api_sender.create_model(
            ModelCreateBody(
                model_name=model_name,
                model_format_code=model_format_code,
                model_upload_uri=model_upload_uri,
                training_id=training_id,
                hyperparameter_tuning_id=hyperparameter_tuning_id,
                description=description,
                parameter_list=parameter_list,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Model create complete. model_id: {self.model_id}")
        if wait:
            self.wait()

        return self

    def create_hugging_face_model(
        self,
        model_name: str,
        description: str | None = None,
        parameter_list: list[Any] | None = None,
        wait: bool | None = True,
    ):
        response = easymaker.easymaker_config.api_sender.create_model(
            ModelCreateBody(
                model_name=model_name,
                model_format_code=ModelFormatCode.HUGGING_FACE,
                description=description,
                parameter_list=parameter_list,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Model create complete. model_id: {self.model_id}")
        if wait:
            self.wait()

        return self
