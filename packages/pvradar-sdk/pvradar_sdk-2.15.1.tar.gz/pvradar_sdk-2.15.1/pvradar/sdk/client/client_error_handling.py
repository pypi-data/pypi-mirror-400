from ..common.exceptions import SerializedError
from ..modeling.basics import DataUnavailableError

_error_mapping = {
    'LookupError': LookupError,
    'NotImplementedError': NotImplementedError,
    'DataUnavailableError': DataUnavailableError,
}


def deserialize_error(error: SerializedError) -> Exception:
    error_class = error.get('error_class', 'Exception')
    detail = error.get('detail', '')
    status = error.get('status', 500)

    exc_class = _error_mapping.get(error_class, Exception)
    exc = exc_class(detail)
    setattr(exc, 'status_code', status)
    return exc
