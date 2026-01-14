import logging
import os

from easymaker.api.api_sender import ApiSender
from easymaker.common import constants

_LOGGER = logging.getLogger(__name__)


class _Config:
    """Stores common parameters and options for API calls."""

    def __init__(self):
        self._appkey = os.environ.get("EM_APPKEY")
        self._region = os.environ.get("EM_REGION")
        self._environment_type = os.environ.get("EM_ENVIRONMENT_TYPE")
        self._user_id = None
        self._access_token = None
        self.api_sender = None
        if os.environ.get("EM_APPKEY") and os.environ.get("EM_REGION"):
            self.api_sender = ApiSender(region=self._region, appkey=self._appkey, environment_type=self._environment_type)

    def init(
        self,
        *,
        appkey: str | None = None,
        region: str | None = None,
        access_token: str | None = None,
        profile: str | None = None,
        experiment_id: str | None = None,
        environment_type: str | None = None,  # 'public' or 'gov'
    ):
        """
        Args:
            appkey (str): easymaker appkey
            region (str): region (kr1, ..)
            access_token (str): easymaker access token
            profile (str): easymaker profile (alpha, beta)
        """
        _LOGGER.debug("EasyMaker Config init")
        if appkey:
            self._appkey = appkey
            os.environ["EM_APPKEY"] = appkey
        if region:
            self._region = region
            os.environ["EM_REGION"] = region
        if access_token:
            self._access_token = access_token
            os.environ["EM_ACCESS_TOKEN"] = access_token
        if profile:
            os.environ["EM_PROFILE"] = profile
        if experiment_id:
            os.environ["EM_EXPERIMENT_ID"] = experiment_id
        if environment_type:
            self._environment_type = environment_type
            os.environ["EM_ENVIRONMENT_TYPE"] = environment_type

        self.api_sender = ApiSender(region, appkey, access_token, environment_type)

    @property
    def appkey(self) -> str:
        return self._appkey

    @property
    def region(self) -> str:
        return self._region or constants.DEFAULT_REGION

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def environment_type(self) -> str:
        return self._environment_type or constants.DEFAULT_ENVIRONMENT_TYPE


# global config to store init parameters: easymaker.init(appkey=..., region=...)
global_config = _Config()
