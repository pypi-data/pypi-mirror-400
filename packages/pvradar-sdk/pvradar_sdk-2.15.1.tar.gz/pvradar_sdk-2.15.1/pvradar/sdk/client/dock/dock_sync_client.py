from typing import Any, Optional, override

from ..engine.engine_types import ModelContextLocator, ModelRecipe
from ..api_query import TimeseriesRequest, Query
from ..sync_client import SyncClient
from ...common.settings import SdkSettings
from ...common.singleton import Singleton
from ...common.pandas_utils import SeriesOrFrame, is_series_or_frame, crop_by_interval
from ...modeling.basics import ResourceTypeExtended
from ...modeling.base_model_context import BaseModelContext
from ...modeling.resource_type_helpers import ResourceTypeClass


class DockSyncClient(SyncClient, Singleton):
    @override
    def get_token(self) -> str:
        return SdkSettings.instance().dock_token

    @override
    def get_base_url(self) -> str:
        return SdkSettings.instance().dock_base_url

    def get_time_series(self, query: TimeseriesRequest | Query) -> SeriesOrFrame:
        if isinstance(query, TimeseriesRequest):
            query = query.as_query()
        return self.get_data_case(query, raise_for_status=False)

    def post_json(self, path: str, json: dict[str, Any]) -> Any:
        r = self.session.post(url=path, json=json)
        return self.extract_json_with_alerts(r)

    def run_engine_model(
        self,
        model_context_locator: ModelContextLocator | BaseModelContext,
        *,
        model_recipe: Optional[ModelRecipe] = None,
        resource: Optional[ResourceTypeExtended] = None,
    ) -> Any:
        if isinstance(model_context_locator, BaseModelContext):
            model_context_locator = model_context_locator.to_model_context_locator()
        payload: dict[str, Any] = {
            'model_context_locator': model_context_locator,
        }
        if model_recipe is not None:
            payload['model_recipe'] = model_recipe
        if resource is not None:
            if isinstance(resource, ResourceTypeClass):
                resource = resource.standard['resource_type']  # pyright: ignore[reportAssignmentType]
            payload['resource'] = resource
        return self.post_data_case('/engine/model-runs', json=payload)


def engine_model(*, context: BaseModelContext, model_name: str, **kwargs) -> Any:
    dock_client = DockSyncClient()

    # make a dictionary from kwargs filtering out everything that is not str or numeric
    filtered_kwargs = {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float))}

    model_recipe: ModelRecipe = {'model_name': model_name, 'params': filtered_kwargs}

    interval = context.get('interval')
    if interval is None:
        raise ValueError('Interval should not be set in context when calling engine model')

    result = dock_client.run_engine_model(
        context.to_model_context_locator(),
        model_recipe=model_recipe,
    )

    if is_series_or_frame(result):
        result = crop_by_interval(result, interval)
    return result
