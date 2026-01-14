from typing import Any, Literal, NotRequired, TypedDict, Union
from httpx import Response


class ApiError(Exception):
    status_code: int
    response: Union[(Response, None)]

    def __init__(self, status_code: int, message: str, response: Union[(Response, None)] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ApiException(ApiError):
    """deprecated, use ApiError instead"""

    pass


class ClientError(Exception):
    response: Union[(Response, None)]

    def __init__(self, message: str, response: Union[(Response, None)] = None):
        super().__init__(message)
        self.response = response


class ClientException(ClientError):
    """deprecated, use ClientError instead"""

    pass


class PvradarSdkError(RuntimeError):
    pass


class PvradarSdkException(PvradarSdkError):
    """deprecated, use PvradarSdkError instead"""

    pass


class SerializedError(TypedDict):
    error_class: str
    status: int  # HTTP status code (part of JSON:API contract)
    detail: str  # message called 'detail' in JSON:API
    meta: NotRequired[dict[str, Any]]


AlertType = Literal['info', 'warning', 'error', 'critical']


class SerializedAlert(TypedDict):
    type: AlertType
    text: str
    html: NotRequired[str]


class OutdatedSdkError(PvradarSdkError):
    pass
