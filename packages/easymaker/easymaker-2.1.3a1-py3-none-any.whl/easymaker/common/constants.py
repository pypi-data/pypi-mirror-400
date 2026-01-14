DEFAULT_REGION = "kr1"
DEFAULT_ENVIRONMENT_TYPE = "public"
EASYMAKER_API_WAIT_INTERVAL_SECONDS = 10

# EasyMaker API URL
EASYMAKER_API_DOMAIN = {
    "public": "nhncloudservice.com",
    "gov": "gov-nhncloudservice.com",
}
EASYMAKER_API_URL_TEMPLATE = "https://{region}-easymaker{profile}.api.{domain}"

# Object Storage URL
OBJECT_STORAGE_TOKEN_URL = {
    "public": "https://api-identity-infrastructure.nhncloudservice.com/v2.0/tokens",
    "gov": "https://api-identity-infrastructure.gov-nhncloudservice.com/v2.0/tokens",
}

# Log & Crash URL
LOGNCRASH_URL = "https://api-logncrash.nhncloudservice.com/v2/log"
LOGNCRASH_MAX_MESSAGE_SIZE = 8000000  # Log&Crash limit body size(= 8388608)
LOGNCRASH_MAX_BUFFER_SIZE = 40000000  # Log&Crash HTTP 요청 하나의 최대 크기 52MB
