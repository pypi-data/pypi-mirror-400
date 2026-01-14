"""
Estimate the output of a PV module at Maximum-Power-Point (MPP) conditions.
"""

from typing import Annotated as A, Optional
import pvlib
import pandas as pd
from ..design.design import InverterDesign, ModuleDesign
from ...modeling.decorators import standard_resource_type, synchronize_freq
from ...modeling import R
from ...modeling.utils import convert_power_to_energy_Wh
from ...modeling.basics import LambdaArgument as LA


@standard_resource_type(R.dc_power, override_unit=True)
@synchronize_freq('default')
def pvlib_pvsystem_pvwatts_dc(
    *,
    effective_poa: A[pd.Series, R.effective_poa(to_unit='W/m^2')],
    cell_temp: A[pd.Series, R.cell_temperature(to_unit='degC')],
    shading_loss_factor: A[Optional[pd.Series], R.shading_loss_factor] = None,
    modules_per_string: A[float, LA(InverterDesign, lambda d: d.modules_per_string)],
    strings_per_inverter: A[float, LA(InverterDesign, lambda d: d.strings_per_inverter)],
    gamma_pdc: A[float, LA(ModuleDesign, lambda d: d.temperature_coefficient_power)],
    module_power: A[float, LA(ModuleDesign, lambda d: d.rated_module_power)],
    ref_temp: float = 25.0,
) -> pd.Series:
    #  g_poa_effective is deprecated in pvlib >= 0.13.0, use effective_irradiance instead
    if pvlib.__version__ >= '0.13.0':
        power_one_module = pvlib.pvsystem.pvwatts_dc(
            effective_irradiance=effective_poa,  # pyright: ignore[reportCallIssue]
            temp_cell=cell_temp,
            pdc0=module_power,
            gamma_pdc=gamma_pdc,
            temp_ref=ref_temp,
        )
    else:
        power_one_module = pvlib.pvsystem.pvwatts_dc(
            g_poa_effective=effective_poa,  # pyright: ignore[reportCallIssue]
            temp_cell=cell_temp,
            pdc0=module_power,
            gamma_pdc=gamma_pdc,
            temp_ref=ref_temp,
        )
    dc_power = power_one_module * modules_per_string * strings_per_inverter
    if shading_loss_factor is not None:
        dc_power = dc_power * (1 - shading_loss_factor)
    return dc_power


@standard_resource_type(R.dc_energy, override_unit=True)
def pvradar_dc_energy_from_power(
    dc_power: A[pd.Series, R.dc_power(to_unit='W')],
):
    return convert_power_to_energy_Wh(dc_power, str(R.dc_power))
