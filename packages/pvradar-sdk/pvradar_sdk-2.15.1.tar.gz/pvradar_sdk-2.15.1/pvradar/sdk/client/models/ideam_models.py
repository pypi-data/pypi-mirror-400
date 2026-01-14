from typing import Annotated as A

import pandas as pd
from pvlib.location import Location
from pydantic import Field as F

from ..api_query import Query
from ...common.pandas_utils import crop_by_interval
from ...modeling import R
from ...modeling.decorators import datasource, standard_resource_type, resource_type
from ..dock.dock_sync_client import DockSyncClient
from ...display.map import GeoLocatedDataFrame


@resource_type(R.meteo_station_table)
@datasource('ideam')
def ideam_meteo_station_table(
    *,
    location: A[Location, F()],
    interval: A[pd.Interval, F()],
    max_distance_km: A[float | None, F()] = 500.0,
) -> pd.DataFrame:
    query = Query.from_site_environment(location=location, interval=interval)
    query['sensor'] = 'rainfall'
    query['max_distance_km'] = max_distance_km
    query.set_path('datasources/ideam/stations')
    df = DockSyncClient().get_data_case(query)
    if 'station_id' in df.columns:
        df.set_index('station_id', inplace=True)

    result = GeoLocatedDataFrame(df)
    return result


@standard_resource_type(R.rainfall)
@datasource('ideam')
def ideam_rainfall(
    *,
    location: A[Location, F()],
    interval: A[pd.Interval, F()],
    station_id: A[str | None, F()] = None,
) -> pd.Series:
    query = Query.from_site_environment(location, interval)
    query['sensor'] = 'rainfall'
    if station_id is not None:
        query['station_id'] = station_id
    query.set_path('datasources/ideam/resources/rainfall')

    series = DockSyncClient().get_data_case(query)
    series = crop_by_interval(series, interval)
    if 'freq' in series.attrs and not series.attrs['freq']:
        del series.attrs['freq']
    return series
