import re
from abc import abstractmethod, ABC
from functools import cached_property
from typing import Any, override

import orjson
from httpx import Client, Response
from httpx._types import QueryParamTypes  # pyright: ignore [reportPrivateImportUsage]
from pandas import DataFrame

from .api_query import Query
from .client_utils import make_timeout_object
from ..common.constants import API_VERSION, SDK_VERSION
from ..common.exceptions import ApiError, ClientError
from ..common.pandas_utils import api_csv_string_to_df
from ..common.settings import SdkSettings
from ..data_case.deserializer import data_case_to_any
from .client_error_handling import deserialize_error
from ..common.logging import log_alert


class SyncClient(ABC):
    @abstractmethod
    def get_token(self) -> str:
        """Returns the token used for authentication."""
        raise NotImplementedError

    @abstractmethod
    def get_base_url(self) -> str:
        """Returns the base URL of the API."""
        raise NotImplementedError

    def __init__(self):
        self._session = None

    @override
    def __repr__(self) -> str:
        return f'<PvradarSyncClient url={self.get_base_url()}>'

    @cached_property
    def session(self) -> Client:
        s = SdkSettings.instance()
        timeout = make_timeout_object()
        session = Client(base_url=self.get_base_url(), timeout=timeout, verify=s.httpx_verify)
        token = self.get_token()
        if token:
            session.headers.update({'Authorization': f'Bearer {token}'})
        session.headers.update({'Accept-version': API_VERSION})
        session.headers.update({'X-PVRADAR-SDK-Version': SDK_VERSION})
        if s.display_alerts:
            session.headers.update({'X-PVRADAR-Capabilities': 'display_alerts'})
        return session

    def get(self, query: str | Query, params: QueryParamTypes | None = None) -> Response:
        if isinstance(query, str):
            return self.session.get(url=query, params=params)
        return self.session.get(url=query.path, params=query.make_query_params())

    def maybe_raise(self, r: Response):
        if r.status_code >= 400:
            raise ApiError(r.status_code, r.text, r)

    def get_csv(self, query: str | Query, params: QueryParamTypes | None = None) -> str:
        r = self.get(query=query, params=params)
        self.maybe_raise(r)
        return r.text

    def get_json(self, query: str | Query, params: QueryParamTypes | None = None, raise_for_status=True) -> dict[str, Any]:
        r = self.get(query=query, params=params)
        return self.extract_json_with_alerts(r, raise_for_status=raise_for_status)

    def _preprocess_json_response(self, json_data: Any) -> Any:
        if isinstance(json_data, dict):
            meta = json_data.get('meta', {})
            assert isinstance(meta, dict), f'meta field must be a dict, got {type(meta)}'
            alerts = meta.get('alerts', [])
            for alert in alerts:
                log_alert(alert)

            errors = json_data.get('errors', [])
            assert isinstance(errors, list), f'errors field must be a list, got {type(meta)}'
            if errors:
                error = deserialize_error(errors[0])  # pyright: ignore[reportArgumentType]
                raise error

    def extract_json_with_alerts(self, r: Response, raise_for_status=True) -> Any:
        json_data = None
        if raise_for_status:
            self.maybe_raise(r)
        else:
            if 'application/json' not in r.headers.get('content-type', ''):
                if r.status_code >= 400:
                    json_data = {
                        'errors': [
                            {
                                'type': 'http_error',
                                'status_code': r.status_code,
                                'detail': f'{r.status_code}: {r.text}',
                            }
                        ]
                    }
                else:
                    raise ClientError(f'expected application/json content type, got: {r.headers.get("content-type")}', r)
        if json_data is None:
            json_data = orjson.loads(r.text)
            self._preprocess_json_response(json_data)

        return json_data

    def get_data_case(self, query: str | Query, params: QueryParamTypes | None = None, raise_for_status=True) -> Any:
        json_data = self.get_json(query, params, raise_for_status=False)

        if 'errors' in json_data:
            error = deserialize_error(json_data['errors'][0])  # pyright: ignore[reportArgumentType]
            raise error

        payload = json_data.get('data')

        if not payload:
            raise ClientError('get_data_case() expects "data" as key for successful response')
        result = data_case_to_any(payload)
        return result

    def get_df(
        self,
        query: str | Query,
        params: QueryParamTypes | None = None,
    ) -> DataFrame:
        r = self.get(query=query, params=params)
        pure_type = re.sub(r';.*$', '', r.headers['content-type']).strip()

        if pure_type in ['application/json']:
            json_data = orjson.loads(r.text)
            self._preprocess_json_response(json_data)

        self.maybe_raise(r)

        if pure_type in ['text/csv', 'application/csv']:
            df = api_csv_string_to_df(r.text, query.tz if isinstance(query, Query) else None)
            settings = SdkSettings.instance()
            if settings.collect_api_metadata:
                df.attrs['api_call'] = {
                    'query': query.as_dict() if isinstance(query, Query) else query,
                    'params': params,
                    'url': str(r.url),
                }
            return df
        raise ClientError(f'unexpected content type: {pure_type}', r)

    def post(
        self,
        subpath: str,
        *,
        json: Any = None,
    ) -> Any:
        return self.session.post(url=subpath, json=json)

    def post_data_case(
        self,
        subpath: str,
        *,
        json: Any = None,
    ) -> Any:
        r = self.post(subpath, json=json)
        json_data = self.extract_json_with_alerts(r, raise_for_status=False)
        payload = json_data.get('data')
        if not payload:
            raise ClientError('post_data_case() expects "data" as key for successful response')
        result = data_case_to_any(payload)
        return result
