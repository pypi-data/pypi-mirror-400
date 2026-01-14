import pvlib
from pvlib.location import Location
from typing import Annotated as A, Literal
import pandas as pd
from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...common.pandas_utils import interval_to_index


@standard_resource_type(R.air_pressure, override_unit=True)
def pvlib_pressure_from_altitude(
    location: Location,
    interval: pd.Interval,
    freq: str,
) -> pd.Series:
    index = interval_to_index(interval, freq)
    pressure_val = pvlib.atmosphere.alt2pres(altitude=location.altitude)
    return pd.Series(pressure_val, index=index)


@standard_resource_type(R.dew_point, override_unit=True)
def pvlib_dew_point_from_rel_hum(
    temp_air: A[pd.Series, R.air_temperature(to_unit='degC')],
    relative_humidity: A[pd.Series, R.relative_humidity(to_unit='%')],
) -> pd.Series:
    dew_point = pvlib.atmosphere.tdew_from_rh(
        temp_air=temp_air,
        relative_humidity=relative_humidity,
    )
    return dew_point


@standard_resource_type(R.airmass, override_unit=True)
def pvlib_airmass(
    solar_zenith: A[pd.Series, R.solar_zenith_angle],
    pressure: A[pd.Series, R.air_pressure(to_unit='Pa')],
    airmass_model: Literal[
        'kastenyoung1989',
        'simple',
        'kasten1966',
        'youngirvine1967',
        'kastenyoung1989',
        'gueymard1993',
        'young1994',
        'pickering2002',
        'gueymard2003',
    ] = 'kastenyoung1989',
) -> pd.Series:
    airmass_at_sea_level = pvlib.atmosphere.get_relative_airmass(
        zenith=solar_zenith,
        model=airmass_model,
    )
    # difference between relative and absolute airmass is pressure correction (mostly due to altitude)
    airmass_at_altitude: pd.Series = pvlib.atmosphere.get_absolute_airmass(
        airmass_relative=airmass_at_sea_level,
        pressure=pressure,  # type: ignore - get_absolute_airmass accepts both float and pd.Series[float]
    )
    return airmass_at_altitude
