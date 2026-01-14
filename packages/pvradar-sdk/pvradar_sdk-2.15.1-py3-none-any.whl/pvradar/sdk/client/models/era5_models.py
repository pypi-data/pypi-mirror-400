from typing import Any, Annotated as A, Literal, Optional

import pandas as pd
from pvlib.location import Location
from pydantic import Field as F

from ..dock.dock_sync_client import DockSyncClient
from ..api_query import Query, TimeseriesRequest
from ..client import ApiError, PvradarClient
from ..pvradar_resources import SeriesConfigAttrs as S
from ...modeling import resource_types as R
from ...modeling.basics import Attrs as P, DataUnavailableError
from ...modeling.decorators import datasource, realign_and_shift_timestamps, standard_resource_type
from ...modeling.model_context import ModelContext
from ...modeling.resource_types._list import standard_mapping
from ...modeling.utils import auto_attr_table

era5_series_name_mapping: dict[str, str | A[Any, Any]] = {
    # ----------------------------------------------------
    # Single levels
    #
    '2m_temperature': A[pd.Series, S(resource_type='air_temperature', unit='degK', agg='mean', freq='1h')],
    'snow_depth': A[
        pd.Series, S(resource_type='snow_depth_water_equivalent', unit='m', agg='mean', freq='1h')
    ],  # snow_depth_water
    'snowfall': A[pd.Series, S(resource_type='snowfall_water_equivalent', unit='m', agg='sum', freq='1h')],  # snowfall_water
    'snow_density': A[pd.Series, S(resource_type='snow_density', unit='kg/m^3', agg='mean', freq='1h')],
    # ----------------------------------------------------
    # Pressure levels
    'relative_humidity': A[pd.Series, S(resource_type='relative_humidity', unit='%', agg='mean', freq='1h')],
}


def _auto_attr_table(df: pd.DataFrame, **kwargs) -> None:
    if df is None:
        return
    auto_attr_table(
        df,
        series_name_mapping=era5_series_name_mapping,
        resource_annotations=standard_mapping,
        **kwargs,
    )
    for name in df:
        df[name].attrs['datasource'] = 'era5'


# ----------------------------------------------------
# ERA5 tables


@standard_resource_type(R.era5_single_level_table)
@datasource('era5')
def era5_single_level_table(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    query = Query.from_site_environment(location=location, interval=interval)
    query.set_path('datasources/era5/raw/hourly/csv')
    result = PvradarClient.instance().get_df(query, crop_interval=interval)

    if not len(result):
        raise DataUnavailableError(interval=interval, where='era5 global dataset')

    _auto_attr_table(result)

    if (
        len(result)
        and interval.left > pd.Timestamp('2005-01-01T00:00:00+05:00')
        and interval.left <= pd.Timestamp('2005-01-01T00:00:00UTC')
    ):
        index = pd.date_range(interval.left, result.index[-1], freq='h')
        original = result
        result = result.reindex(index)
        result = result.bfill()
        # workaround for bug in pandas overwriting attrs
        for column in result.columns:
            result[column].attrs = original[column].attrs

    return result


# ----------------------------------------------------
# ERA5 series (alphabetical order)
Era5DatasetName = Literal[
    'era5-land',
    'era5-global',
    # 'era5-single-levels', 'era5-pressure-levels'
]
era5_datasets_priority: list[Era5DatasetName] = ['era5-land', 'era5-global']


def get_series_from_dock(
    *,
    location: Location,
    interval: pd.Interval,
    resource_type_name: str,
    unit: Optional[str],
    dataset: Optional[Era5DatasetName],
) -> pd.Series:
    ts_request = TimeseriesRequest(
        resource_type=resource_type_name,  # pyright: ignore [reportArgumentType]
        location=location,
        interval=interval,
        dataset=dataset,
        datasource='era5',
    )
    query = ts_request.as_query()
    result = DockSyncClient().get_time_series(query)
    if unit is not None:
        if result.attrs.get('unit') != unit:
            raise ValueError(f'Unexpected unit for {resource_type_name}: {result.attrs.get("unit")}, expected: {unit}')
    return result


def get_series_from_outlet(
    *,
    location: Location,
    interval: pd.Interval,
    resource_type_name: str,
    unit: Optional[str],
    dataset: Optional[Era5DatasetName],
) -> pd.Series:
    query = Query.from_site_environment(location=location, interval=interval)
    query['sensors'] = resource_type_name
    query.set_path('datasources/era5/data')
    exception = None
    for priority_dataset in [dataset] if dataset else era5_datasets_priority:
        query['dataset_name'] = priority_dataset
        try:
            result = PvradarClient.instance().get_df(query, crop_interval=interval)[resource_type_name]
            if unit is not None:
                result.attrs['unit'] = unit
            result.attrs['dataset'] = priority_dataset
            return result
        except ApiError as e:
            try:
                if e.status_code == 422 and 'not available' in str(e):
                    raise DataUnavailableError(str(e)) from e
                raise e
            except Exception as e:
                exception = e
                continue
    if exception:
        raise exception
    raise AssertionError('This should never happen, but if it does, please report it.')


def make_land_series(
    *,
    location: Location,
    interval: pd.Interval,
    resource_type_name: str,
    unit: Optional[str] = None,
) -> pd.Series:
    return get_series_from_dock(
        location=location,
        interval=interval,
        resource_type_name=resource_type_name,
        unit=unit,
        dataset='era5-land',
    )


def make_global_series(
    *,
    location: Location,
    interval: pd.Interval,
    resource_type_name: str,
    unit: Optional[str],
) -> pd.Series:
    return get_series_from_outlet(
        location=location,
        interval=interval,
        resource_type_name=resource_type_name,
        unit=unit,
        dataset='era5-global',
    )


# ----------------------------------------------------
# ERA5 resource models


@standard_resource_type(R.total_precipitation, use_default_freq=True)
@datasource('era5')
def era5_total_precipitation(
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    return make_land_series(
        location=location,
        interval=interval,
        resource_type_name='total_precipitation',
    )


@standard_resource_type(R.rainfall, use_default_freq=True)
@datasource('era5')
def era5_rainfall(
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    return era5_total_precipitation(
        location=location,
        interval=interval,
        dataset=dataset,
    )


@standard_resource_type(R.global_horizontal_irradiance, use_default_freq=True)
@datasource('era5')
def era5_global_horizontal_irradiance(
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    return make_land_series(
        location=location,
        interval=interval,
        resource_type_name='global_horizontal_irradiance',
    )


@realign_and_shift_timestamps()
@standard_resource_type(R.uv_horizontal_irradiance, use_default_freq=True)
@datasource('era5')
def era5_uv_horizontal_irradiance(
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-global', None], F()] = None,  # nothing in era5-land
) -> pd.Series:
    return (
        make_global_series(
            location=location,
            interval=interval,
            resource_type_name='uv_horizontal_irradiance',
            unit='W/m^2',
            # converting J/hour/m^2 into W/m^2
        )
        / 3600
    )


@standard_resource_type(R.air_temperature, use_default_freq=True)
@datasource('era5')
def era5_air_temperature(
    *,
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    return make_land_series(
        location=location,
        interval=interval,
        resource_type_name='air_temperature',
    )


@realign_and_shift_timestamps()
@standard_resource_type(R.relative_humidity, use_default_freq=True)
@datasource('era5')
def era5_relative_humidity(
    *,
    era5_single_level_table: A[pd.DataFrame, P(resource_type='era5_single_level_table')],
    dataset: A[Literal['era5-global', None], F()] = None,  # nothing in era5-land
) -> pd.Series:
    series = era5_single_level_table['relative_humidity']
    if series.attrs['unit'] != '%':
        raise ValueError(f'Unexpected unit: {series.attrs["unit"]}')
    series_copy = series.copy()
    series_copy.attrs['dataset'] = dataset or 'era5-global'
    return series_copy


@standard_resource_type(R.snow_density, use_default_freq=True)
@datasource('era5')
def era5_snow_density(
    *,
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    return make_land_series(
        location=location,
        interval=interval,
        resource_type_name='snow_density',
    )


@standard_resource_type(R.snow_depth_water_equivalent, use_default_freq=True)
@datasource('era5')
def era5_snow_depth_water_equivalent(
    *,
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    return make_land_series(
        location=location,
        interval=interval,
        resource_type_name='snow_depth_water_equivalent',
    )


@standard_resource_type(R.snow_depth, use_default_freq=True)
@datasource('era5')
def era5_snow_depth(
    *,
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    return make_land_series(
        location=location,
        interval=interval,
        resource_type_name='snow_depth',
        unit='m',
    )


@standard_resource_type(R.snowfall_water_equivalent, use_default_freq=True)
@datasource('era5')
def era5_snowfall_water_equivalent(
    *,
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    return make_land_series(
        location=location,
        interval=interval,
        resource_type_name='snowfall_water_equivalent',
    )


@standard_resource_type(R.snowfall, use_default_freq=True)
@datasource('era5')
def era5_snowfall(
    *,
    context: ModelContext,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    era5_snowfall_water_equivalent = context.resource(R.snowfall_water_equivalent(datasource='era5', dataset=dataset))
    snow_density_value = 100  # Kg/m^3, value for fresh snow
    water_density = 1000
    result = era5_snowfall_water_equivalent * (water_density / snow_density_value)
    result.attrs['agg'] = 'sum'
    result.attrs['dataset'] = era5_snowfall_water_equivalent.attrs['dataset']
    return result


@standard_resource_type(R.wind_speed, use_default_freq=True)
@datasource('era5')
def era5_wind_speed(
    *,
    location: Location,
    interval: pd.Interval,
    dataset: A[Literal['era5-land', None], F()] = None,  # nothing in era5-global
) -> pd.Series:
    u10m = make_land_series(
        location=location,
        interval=interval,
        resource_type_name='u10m_wind_component',
    )
    v10m = make_land_series(
        location=location,
        interval=interval,
        resource_type_name='v10m_wind_component',
    )
    result = (u10m**2 + v10m**2) ** 0.5
    result.attrs['dataset'] = u10m.attrs['dataset']
    return result
