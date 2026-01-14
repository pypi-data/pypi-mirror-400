"""
Estimate the temperature of the PV module back surface ('module') or photovoltaic cells ('cell') during operation.
"""

from ...modeling.decorators import standard_resource_type, synchronize_freq
from ...modeling import R
from typing import Annotated as A
import pandas as pd
from pydantic import Field
from pvlib.temperature import (
    sapm_module,
    sapm_cell_from_module,
    pvsyst_cell,
)


### --- CELL TEMPERATURE --- ###


@standard_resource_type(R.cell_temperature, override_unit=True)
@synchronize_freq('default')
def pvlib_temperature_sapm_cell_from_module(
    module_temp: A[pd.Series, R.module_temperature(to_unit='degC')],
    effective_poa: A[pd.Series, R.effective_poa(to_unit='W/m^2')],
    deltaT_module_cell: A[float, Field(ge=0)] = 3,
) -> pd.Series:
    """
    Wrapper around the PVLIB implementation of the Sandia Array Performance Model (SAPM) cell temperature model.
    """
    cell_temperature = sapm_cell_from_module(
        module_temperature=module_temp,
        poa_global=effective_poa,
        deltaT=deltaT_module_cell,
    )
    return cell_temperature


@standard_resource_type(R.cell_temperature, override_unit=True)
@synchronize_freq('default')
def pvlib_temperature_pvsyst_cell(
    effective_poa: A[pd.Series, R.effective_poa(to_unit='W/m^2')],
    air_temp: A[pd.Series, R.air_temperature(to_unit='degC')],
    wind_speed: A[pd.Series, R.wind_speed(to_unit='m/s')],
    temp_coef_u_c: A[float, Field(ge=0)] = 29,
    temp_coef_u_v: A[float, Field(ge=0)] = 0,
    module_eff_value: A[float, Field(gt=0)] = 0.1,
    module_alpha_absorption: A[float, Field(gt=0)] = 0.9,
) -> pd.Series:
    """
    Wrapper around the PVLIB implementation of the PVSYST cell temperature model.
    """
    cell_temperature = pvsyst_cell(
        poa_global=effective_poa,
        temp_air=air_temp,
        wind_speed=wind_speed,  # type: ignore - can be both float and pd.Series although typehint asks for float
        u_c=temp_coef_u_c,
        u_v=temp_coef_u_v,
        module_efficiency=module_eff_value,
        alpha_absorption=module_alpha_absorption,
    )
    return cell_temperature


### --- MODULE TEMPERATURE --- ###


@standard_resource_type(R.module_temperature, override_unit=True)
@synchronize_freq('default')
def pvlib_temperature_sapm_module(
    effective_poa: A[pd.Series, R.effective_poa(to_unit='W/m^2')],
    air_temp: A[pd.Series, R.air_temperature(to_unit='degC')],
    wind_speed: A[pd.Series, R.wind_speed(to_unit='m/s')],
    sapm_temp_a: float = -3.56,
    sapm_temp_b: float = -0.075,
) -> pd.Series:
    """
    Wrapper around the PVLIB implementation of the Sandia Array Performance Model (SAPM) module temperature model.
    """
    module_temperature = sapm_module(
        poa_global=effective_poa,
        temp_air=air_temp,
        wind_speed=wind_speed,
        a=sapm_temp_a,
        b=sapm_temp_b,
    )
    return module_temperature
