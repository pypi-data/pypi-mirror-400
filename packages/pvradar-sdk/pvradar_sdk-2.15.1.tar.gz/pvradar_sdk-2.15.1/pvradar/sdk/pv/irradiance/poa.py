from typing import Literal, Annotated as A, Optional
import pandas as pd
import pvlib

from ...modeling.basics import LambdaArgument as LA
from ..design.design import ArrayDesign, ModuleDesign, StructureDesign
from ...modeling.decorators import standard_resource_type, synchronize_freq
from ...modeling import R


ModuleSide = Literal['both', 'front', 'back']


### --- GLOBAL PLANE OF ARRAY IRRADIANCE --- ###


@standard_resource_type(R.global_poa_on_front, override_unit=True)
@synchronize_freq('default')
def sum_global_poa_on_front(
    ground_diffuse_poa_on_front: A[pd.Series, R.ground_diffuse_poa_on_front(to_unit='W/m^2')],
    sky_diffuse_poa_on_front: A[pd.Series, R.sky_diffuse_poa_on_front(to_unit='W/m^2')],
    direct_poa_on_front: A[pd.Series, R.direct_poa_on_front(to_unit='W/m^2')],
) -> pd.Series:
    """
    The global irradiance on the front side of a tilted or tracked pv module.
    'global' means sum of all components but without losses.
    """
    global_on_front = ground_diffuse_poa_on_front + sky_diffuse_poa_on_front + direct_poa_on_front
    global_on_front = global_on_front.fillna(0)
    if 'datasource' in global_on_front.attrs:
        del global_on_front.attrs['datasource']
    return global_on_front


@synchronize_freq('default')
@standard_resource_type(R.global_poa_on_back)
def pvlib_global_poa_on_back(
    surface_tilt: A[pd.Series, R.surface_tilt_angle],
    surface_azimuth: A[pd.Series, R.surface_azimuth_angle],
    solar_zenith: A[pd.Series, R.solar_zenith_angle],
    solar_azimuth: A[pd.Series, R.solar_azimuth_angle],
    ghi: A[pd.Series, R.global_horizontal_irradiance(to_unit='W/m^2')],
    dhi: A[pd.Series, R.diffuse_horizontal_irradiance(to_unit='W/m^2')],
    dni: A[pd.Series, R.direct_normal_irradiance(to_unit='W/m^2')],
    dni_extra: A[pd.Series, R.extraterrestrial_radiation(to_unit='W/m^2')],
    albedo_value: A[float, LA(ArrayDesign, lambda d: d.albedo_value)],
    ground_cover_ratio: A[float, LA(ArrayDesign, lambda d: d.ground_cover_ratio)],
    collector_height: A[float, LA(StructureDesign, lambda d: d.collector_height)],
    pitch: A[float, LA(ArrayDesign, lambda d: d.pitch)],
):
    # backside is rotated and flipped relative to front
    backside_tilt, backside_sysaz = pvlib.bifacial.infinite_sheds._backside(surface_tilt, surface_azimuth)
    # front side POA irradiance

    # back side POA irradiance
    irrad_back = pvlib.bifacial.infinite_sheds.get_irradiance_poa(
        surface_tilt=backside_tilt,
        surface_azimuth=backside_sysaz,
        solar_zenith=solar_zenith,
        solar_azimuth=solar_azimuth,
        gcr=ground_cover_ratio,
        height=collector_height,
        pitch=pitch,
        ghi=ghi,
        dhi=dhi,
        dni=dni,
        albedo=albedo_value,
        model='haydavies',
        dni_extra=dni_extra,
        iam=1.0,  # assumption: no back side reflection losses
        npoints=100,
        vectorize=True,
    )
    return irrad_back['poa_global']


@standard_resource_type(R.global_poa, override_unit=True)
@synchronize_freq('default')
def sum_global_poa(
    poa_on_front: A[pd.Series, R.global_poa_on_front(to_unit='W/m^2')],
    poa_on_rear: A[pd.Series, R.global_poa_on_back(to_unit='W/m^2')],
) -> pd.Series:
    return poa_on_front + poa_on_rear


### --- EFFECTIVE POA IRRADIANCE --- ###
@standard_resource_type(R.effective_poa, override_unit=True)
@synchronize_freq('default')
def pvradar_effective_poa(
    *,
    # required
    ground_diffuse_poa_on_front: A[pd.Series, R.ground_diffuse_poa_on_front(to_unit='W/m^2')],
    sky_diffuse_poa_on_front: A[pd.Series, R.sky_diffuse_poa_on_front(to_unit='W/m^2')],
    direct_poa_on_front: A[pd.Series, R.direct_poa_on_front(to_unit='W/m^2')],
    # time series loss factors (optional)
    poa_on_back: A[Optional[pd.Series], R.global_poa_on_back(to_unit='W/m^2')] = None,
    soiling_loss_factor: A[Optional[pd.Series], R.soiling_loss_factor] = None,
    snow_loss_factor: A[Optional[pd.Series], R.snow_loss_factor] = None,
    reflection_loss_factor: A[Optional[pd.Series], R.reflection_loss_factor] = None,
    # single value loss factors (optional)
    bifaciality_factor: A[Optional[float], LA(ModuleDesign, lambda d: d.bifaciality_factor)],
    back_shading_loss_factor: A[Optional[float], LA(StructureDesign, lambda d: d.back_shading_loss_factor)],
    back_mismatch_loss_factor: A[Optional[float], LA(StructureDesign, lambda d: d.back_mismatch_loss_factor)],
    back_transmission_loss_factor: A[Optional[float], LA(ModuleDesign, lambda d: d.back_transmission_loss_factor)],
) -> pd.Series:
    ## ---- Effective POA on front ----
    effective_on_front = ground_diffuse_poa_on_front + sky_diffuse_poa_on_front

    if reflection_loss_factor is not None:
        effective_on_front = effective_on_front + (direct_poa_on_front * (1 - reflection_loss_factor))
    else:
        effective_on_front = effective_on_front + direct_poa_on_front

    if soiling_loss_factor is not None:
        effective_on_front = effective_on_front * (1 - soiling_loss_factor)

    if snow_loss_factor is not None:
        effective_on_front = effective_on_front * (1 - snow_loss_factor)

    ## ---- Effective POA on back ----
    if poa_on_back is not None and not (bifaciality_factor is None or bifaciality_factor == 0):
        effective_on_back = poa_on_back

        if back_shading_loss_factor is not None:
            effective_on_back = effective_on_back * (1 - back_shading_loss_factor)

        if back_mismatch_loss_factor is not None:
            effective_on_back = effective_on_back * (1 - back_mismatch_loss_factor)

        if back_transmission_loss_factor is not None:
            effective_on_back = effective_on_back * (1 - back_transmission_loss_factor)

        return effective_on_front + (effective_on_back * bifaciality_factor)

    return effective_on_front


@standard_resource_type(R.effective_poa, override_unit=True)
@synchronize_freq('default')
def pvradar_effective_poa_from_global_front_poa(
    *,
    # required
    poa_on_front: A[pd.Series, R.global_poa_on_front(to_unit='W/m^2')],
    # time series loss factors (optional)
    poa_on_back: A[Optional[pd.Series], R.global_poa_on_back(to_unit='W/m^2')] = None,
    soiling_loss_factor: A[Optional[pd.Series], R.soiling_loss_factor] = None,
    snow_loss_factor: A[Optional[pd.Series], R.snow_loss_factor] = None,
    reflection_loss_factor: A[Optional[pd.Series], R.reflection_loss_factor] = None,
    # single value loss factors (optional)
    bifaciality_factor: A[Optional[float], LA(ModuleDesign, lambda d: d.bifaciality_factor)],
    back_shading_loss_factor: A[Optional[float], LA(StructureDesign, lambda d: d.back_shading_loss_factor)],
    back_mismatch_loss_factor: A[Optional[float], LA(StructureDesign, lambda d: d.back_mismatch_loss_factor)],
    back_transmission_loss_factor: A[Optional[float], LA(ModuleDesign, lambda d: d.back_transmission_loss_factor)],
) -> pd.Series:
    ## ---- Effective POA on front ----
    effective_on_front = poa_on_front

    if reflection_loss_factor is not None:
        effective_on_front = effective_on_front * (1 - reflection_loss_factor)

    if soiling_loss_factor is not None:
        effective_on_front = effective_on_front * (1 - soiling_loss_factor)

    if snow_loss_factor is not None:
        effective_on_front = effective_on_front * (1 - snow_loss_factor)

    ## ---- Effective POA on back ----
    if poa_on_back is not None and not (bifaciality_factor is None or bifaciality_factor == 0):
        effective_on_back = poa_on_back

        if back_shading_loss_factor is not None:
            effective_on_back = effective_on_back * (1 - back_shading_loss_factor)

        if back_mismatch_loss_factor is not None:
            effective_on_back = effective_on_back * (1 - back_mismatch_loss_factor)

        if back_transmission_loss_factor is not None:
            effective_on_back = effective_on_back * (1 - back_transmission_loss_factor)

        return effective_on_front + (effective_on_back * bifaciality_factor)

    return effective_on_front
