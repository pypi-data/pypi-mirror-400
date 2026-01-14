from typing import Annotated as A
import pandas as pd
import pvlib
from pvlib.location import Location
from pydantic import Field

from ...common.pandas_utils import interval_to_index
from ...modeling.decorators import standard_resource_type
from ...modeling import R, LambdaArgument as LA
from ..design.design import ArrayDesign
from ...modeling.decorators import synchronize_freq

### --- EXTRATERRESTRIAL RADIATION --- ###


@standard_resource_type(R.extraterrestrial_radiation, override_unit=True)
def pvlib_irradiance_get_extra_radiation(
    interval: pd.Interval,
    freq: str,
) -> pd.Series:
    """
    The extraterrestrial solar radiation at the top of Earth's atmosphere accounting for
    Earth's orbital variations. Returns a series of values around 1300 - 1400 W/m^2.
    """
    timestamps = interval_to_index(interval, freq=freq)
    extraterrestrial_radiation = pvlib.irradiance.get_extra_radiation(
        datetime_or_doy=timestamps,
        method='spencer',
    )
    return extraterrestrial_radiation  # type: ignore


### --- CLEARNESS & ClEARSKY INDEX --- ###


@synchronize_freq('default')
@standard_resource_type(R.clearness_index, override_unit=True)
def pvlib_clearness_index(
    ghi: A[pd.Series, R.global_horizontal_irradiance(to_unit='W/m^2')],
    solar_zenith_angle: A[pd.Series, R.solar_zenith_angle(apparent=False)],
    extra_radiation: A[pd.Series, R.extraterrestrial_radiation(to_unit='W/m^2')],
    min_cos_zenith: A[float, Field(ge=0, le=1.0)] = 0.065,
    max_clearness_index: float = 2,
) -> pd.Series:
    clearness_index = pvlib.irradiance.clearness_index(
        ghi=ghi,
        solar_zenith=solar_zenith_angle,
        extra_radiation=extra_radiation,
        min_cos_zenith=min_cos_zenith,
        max_clearness_index=max_clearness_index,
    )
    return clearness_index


def pvlib_clearsky_table(
    apparent_zenith: A[pd.Series, R.solar_zenith_angle(apparent=True)],
    airmass: A[pd.Series, R.airmass],
    dni_extra: A[pd.Series, R.extraterrestrial_radiation(to_unit='W/m^2')],
    location: Location,
    interval: pd.Interval,
    freq: str,
) -> pd.DataFrame:
    linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(
        time=interval_to_index(interval, freq),
        latitude=location.latitude,
        longitude=location.longitude,
        interp_turbidity=True,
    )
    clearsky_table: pd.DataFrame = pvlib.clearsky.ineichen(
        apparent_zenith=apparent_zenith,
        airmass_absolute=airmass,
        linke_turbidity=linke_turbidity,
        altitude=location.altitude,  # type: ignore
        dni_extra=dni_extra,  # type: ignore
        perez_enhancement=False,
    )
    return clearsky_table


### --- IRRADIANCE ON GROUND --- ###
"""
Components are:
- direct normal irradiance (DNI)
- diffuse horizontal irradiance (DHI)
- global horizontal irradiance (GHI)
"""


@standard_resource_type(R.direct_normal_irradiance, override_unit=True)
@synchronize_freq('default')
def pvlib_irradiance_dirint(
    global_horizontal_irradiance: A[pd.Series, R.global_horizontal_irradiance(to_unit='W/m^2')],
    solar_zenith_angle: A[pd.Series, R.solar_zenith_angle],
    interval: pd.Interval,
    freq: str,
) -> pd.Series:
    direct_normal_irradiance = pvlib.irradiance.dirint(
        ghi=global_horizontal_irradiance,
        solar_zenith=solar_zenith_angle,
        times=interval_to_index(interval, freq=freq),
        temp_dew=None,  # TODO: pass dew point temperature for correction
    )
    # pvlib.irradiance.dirint produces NaN when sun elevation < 0 meaning sun is under horizon line
    direct_normal_irradiance = direct_normal_irradiance.fillna(0)
    return direct_normal_irradiance


@standard_resource_type(R.diffuse_horizontal_irradiance, override_unit=True)
@synchronize_freq('default')
def pvlib_irradiance_complete_irradiance(
    global_horizontal_irradiance: A[pd.Series, R.global_horizontal_irradiance(to_unit='W/m^2')],
    direct_normal_irradiance: A[pd.Series, R.direct_normal_irradiance(to_unit='W/m^2')],
    solar_zenith_angle: A[pd.Series, R.solar_zenith_angle],
) -> pd.Series:
    irradiation_components_table = pvlib.irradiance.complete_irradiance(
        solar_zenith=solar_zenith_angle, ghi=global_horizontal_irradiance, dni=direct_normal_irradiance
    )
    return irradiation_components_table['dhi']


### --- POA IRRADIANCE COMPONENTS --- ###
"""
Components are:
- ground reflected on front
- sky diffuse on front
- direct on front
- ground reflecteed on rear
"""


@standard_resource_type(R.ground_diffuse_poa_on_front, override_unit=True)
@synchronize_freq('default')
def pvlib_irradiance_get_ground_diffuse(
    surface_tilt: A[pd.Series, R.surface_tilt_angle],
    global_horizontal_irradiance: A[pd.Series, R.global_horizontal_irradiance(to_unit='W/m^2')],
    albedo_value: A[float, LA(ArrayDesign, lambda d: d.albedo_value)],
) -> pd.Series:
    ground_diffuse_poa_on_front = pvlib.irradiance.get_ground_diffuse(
        surface_tilt=surface_tilt,
        ghi=global_horizontal_irradiance.values,
        albedo=albedo_value,
    )
    return ground_diffuse_poa_on_front


@standard_resource_type(R.sky_diffuse_poa_on_front, override_unit=True)
@synchronize_freq('default')
def pvlib_irradiance_perez_driesse(
    surface_tilt: A[pd.Series, R.surface_tilt_angle],
    surface_azimuth: A[pd.Series, R.surface_azimuth_angle],
    diffuse_horizontal_irradiance: A[pd.Series, R.diffuse_horizontal_irradiance(to_unit='W/m^2')],
    direct_normal_irradiance: A[pd.Series, R.direct_normal_irradiance(to_unit='W/m^2')],
    extraterrestrial_radiation: A[pd.Series, R.extraterrestrial_radiation(to_unit='W/m^2')],
    solar_zenith_angle: A[pd.Series, R.solar_zenith_angle],
    solar_azimuth_angle: A[pd.Series, R.solar_azimuth_angle],
) -> pd.Series:
    """
    Sum of isotropic, horizon, and circumsolar
    """
    sky_diffuse_poa_on_front = pvlib.irradiance.perez_driesse(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        dhi=diffuse_horizontal_irradiance,
        dni=direct_normal_irradiance,
        dni_extra=extraterrestrial_radiation,
        solar_zenith=solar_zenith_angle,
        solar_azimuth=solar_azimuth_angle,
        airmass=None,
        return_components=False,
    )
    return sky_diffuse_poa_on_front  # type: ignore


@standard_resource_type(R.sky_diffuse_poa_on_front, override_unit=True)
@synchronize_freq('default')
def pvlib_irradiance_haydavies(
    surface_tilt: A[pd.Series, R.surface_tilt_angle],
    surface_azimuth: A[pd.Series, R.surface_azimuth_angle],
    diffuse_horizontal_irradiance: A[pd.Series, R.diffuse_horizontal_irradiance(to_unit='W/m^2')],
    direct_normal_irradiance: A[pd.Series, R.direct_normal_irradiance(to_unit='W/m^2')],
    extraterrestrial_radiation: A[pd.Series, R.extraterrestrial_radiation(to_unit='W/m^2')],
    solar_zenith_angle: A[pd.Series, R.solar_zenith_angle],
    solar_azimuth_angle: A[pd.Series, R.solar_azimuth_angle],
) -> pd.Series:
    """
    Sum of isotropic, horizon, and circumsolar
    """
    sky_diffuse_poa_on_front = pvlib.irradiance.haydavies(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        dhi=diffuse_horizontal_irradiance,
        dni=direct_normal_irradiance,
        dni_extra=extraterrestrial_radiation,
        solar_zenith=solar_zenith_angle,
        solar_azimuth=solar_azimuth_angle,
        projection_ratio=None,
        return_components=False,
    )
    return sky_diffuse_poa_on_front  # type: ignore


@standard_resource_type(R.direct_poa_on_front, override_unit=True)
@synchronize_freq('default')
def pvlib_irradiance_beam_component(
    surface_tilt: A[pd.Series, R.surface_tilt_angle],
    surface_azimuth: A[pd.Series, R.surface_azimuth_angle],
    solar_zenith_angle: A[pd.Series, R.solar_zenith_angle],
    solar_azimuth_angle: A[pd.Series, R.solar_azimuth_angle],
    direct_normal_irradiance: A[pd.Series, R.direct_normal_irradiance(to_unit='W/m^2')],
) -> pd.Series:
    direct_poa_on_front = pvlib.irradiance.beam_component(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        solar_zenith=solar_zenith_angle,
        solar_azimuth=solar_azimuth_angle,
        dni=direct_normal_irradiance,
    )
    return direct_poa_on_front


# # TODO: fully implement this function based on pvfactors
# @standard_resource_type(R.ground_diffuse_poa_on_back, override_unit=True)
# def ground_diffuse_poa_on_back(interval: pd.Interval) -> pd.Series:
#     timestamps = interval_to_index(interval)
#     ground_diffuse_poa_on_back = pd.Series(index=timestamps, data=[0] * len(timestamps))
#     return ground_diffuse_poa_on_back
