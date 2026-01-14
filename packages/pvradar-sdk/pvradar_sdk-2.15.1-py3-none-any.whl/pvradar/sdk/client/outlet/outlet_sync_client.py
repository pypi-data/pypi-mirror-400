from typing import Any, Self, override
import warnings
from httpx import Client

from ...common.settings import SdkSettings
from ...common.exceptions import PvradarSdkException
from ..sync_client import SyncClient

default_url = 'https://api.pvradar.com/v2'
_client_instances: dict[str, Any] = {}


class OutletSyncClient(SyncClient):
    _token: str
    _base_url: str
    _session: Client | None

    def __init__(
        self,
        token: str = 'pvradar_public',
        base_url: str = default_url,
    ):
        self._token = token
        self._base_url = base_url
        self._session = None

    @override
    def __repr__(self) -> str:
        return f'<PvradarSyncClient url={self._base_url}>'

    @override
    def get_token(self) -> str:
        return self._token

    @override
    def get_base_url(self) -> str:
        return self._base_url

    @classmethod
    def from_config(cls, config_path_str='') -> Self:
        if config_path_str:
            raise PvradarSdkException('from_config() is deprecated and config_path_str is no longer supported')
        warnings.warn('from_config() is deprecated. Use instance() or OutletSyncClient(...)', DeprecationWarning)
        settings = SdkSettings.instance()
        return cls(
            token=settings.outlet_token,
            base_url=settings.outlet_base_url,
        )

    @classmethod
    def instance(cls, base_url: str = '', **kwargs) -> Self:
        if base_url:
            raise PvradarSdkException('instance(base_url) is is no longer supported, please use without parameters')
        settings = SdkSettings.instance()
        id = str(settings.outlet_base_url)
        global _client_instances
        _client_instance = _client_instances.get(id)
        if not _client_instance:
            _client_instance = cls(base_url=base_url, token=settings.outlet_token)
            _client_instances[id] = _client_instance
        return _client_instance
