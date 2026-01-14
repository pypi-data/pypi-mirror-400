"""
Estimate the inverter power output.
"""

from typing import Annotated as A
import pvlib
import pandas as pd
from ..design.design import InverterDesign
from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...modeling.utils import convert_power_to_energy_Wh
from ...modeling.basics import LambdaArgument as LA
from pydantic import Field


@standard_resource_type(R.inverter_power, override_unit=True)
def pvlib_inverter_pvwatts(
    dc_power: A[pd.Series, R.dc_power(to_unit='W')],
    rated_inverter_power: A[float, LA(InverterDesign, lambda d: d.rated_inverter_power_ac)],
    nom_inv_eff: A[float, LA(InverterDesign, lambda d: d.nominal_efficiency)],
    ref_inv_eff: A[float, Field(gt=0)] = 0.9637,
) -> pd.Series:
    """
    This simplified model describes all inverters as one big inverter connected to the all dc modules.
    """
    inverter_power = pvlib.inverter.pvwatts(
        pdc=dc_power,
        pdc0=rated_inverter_power,
        eta_inv_nom=nom_inv_eff,
        eta_inv_ref=ref_inv_eff,
    )
    return inverter_power


@standard_resource_type(R.inverter_energy, override_unit=True)
def pvradar_inverter_energy_from_power(
    inverter_power: A[pd.Series, R.inverter_power(to_unit='W')],
):
    return convert_power_to_energy_Wh(inverter_power, str(R.inverter_energy))
