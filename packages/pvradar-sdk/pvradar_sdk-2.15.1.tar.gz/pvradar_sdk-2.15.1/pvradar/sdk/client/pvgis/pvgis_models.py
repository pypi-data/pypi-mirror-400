from typing import Annotated as A, Optional
import pandas as pd
from pydantic import Field

from .pvgis_client import PvgisDatabase
from ..api_query import TimeseriesRequest
from pvlib.location import Location
from ...modeling.decorators import datasource, standard_resource_type
from ...modeling import R
from ..dock.dock_sync_client import DockSyncClient

# ----------------------------------------------------
# PVGIS tables


@standard_resource_type(R.pvgis_seriescalc_table)
@datasource('pvgis')
def pvgis_seriescalc_table(
    *,
    location: A[Location, Field()],
    interval: A[pd.Interval, Field()],
    dataset: A[Optional[PvgisDatabase], Field()] = None,
) -> pd.DataFrame:
    ts_request = TimeseriesRequest(
        datasource='pvgis',
        resource_type=R.pvgis_seriescalc_table,
        location=location,
        interval=interval,
        dataset=dataset,
    )
    query = ts_request.as_query()
    return DockSyncClient().get_time_series(query)


# ----------------------------------------------------
# PVGIS series (alphabetical order)
# here and below the unused 'dataset' parameter is used for automatic validation


@standard_resource_type(R.air_temperature, use_default_freq=True)
@datasource('pvgis')
def pvgis_air_temperature(
    *,
    pvgis_seriescalc_table: A[pd.DataFrame, R.pvgis_seriescalc_table],
    dataset: A[Optional[PvgisDatabase], Field()] = None,
) -> pd.Series:
    return pvgis_seriescalc_table['T2m']


@standard_resource_type(R.global_horizontal_irradiance, use_default_freq=True)
@datasource('pvgis')
def pvgis_global_horizontal_irradiance(
    *,
    pvgis_seriescalc_table: A[pd.DataFrame, R.pvgis_seriescalc_table],
    dataset: A[Optional[PvgisDatabase], Field()] = None,
) -> pd.Series:
    result = pvgis_seriescalc_table['G(i)']
    # result = resample_series(result, freq=freq, interval=interval)
    return result


@standard_resource_type(R.wind_speed, use_default_freq=True)
@datasource('pvgis')
def pvgis_wind_speed(
    *,
    pvgis_seriescalc_table: A[pd.DataFrame, R.pvgis_seriescalc_table],
    dataset: A[Optional[PvgisDatabase], Field()] = None,
) -> pd.Series:
    return pvgis_seriescalc_table['WS10m']
