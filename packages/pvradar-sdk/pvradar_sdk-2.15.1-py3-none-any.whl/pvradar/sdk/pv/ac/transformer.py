from typing import Annotated as A
import pvlib
import pandas as pd
import pvlib.transformer

from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...modeling.utils import convert_power_to_energy_Wh
from ...modeling.basics import LambdaArgument as LA
from ...pv.design.design import TransformerDesign, ArrayDesign


@standard_resource_type(R.ac_power, override_unit=True)
def pvlib_transformer_simple_efficiency(
    inverter_power: A[pd.Series, R.inverter_power(to_unit='W')],
    no_load_loss: A[float, LA(TransformerDesign, lambda d: d.no_load_loss)],
    full_load_loss: A[float, LA(TransformerDesign, lambda d: d.full_load_loss)],
    rated_array_power: A[float, LA(ArrayDesign, lambda d: d.rated_array_power_ac)],
    inverter_count: A[float, LA(ArrayDesign, lambda d: d.inverter_count)],
) -> pd.Series:
    input_power = inverter_power * inverter_count
    ac_power = pvlib.transformer.simple_efficiency(
        input_power=input_power,
        no_load_loss=no_load_loss,
        load_loss=full_load_loss,
        transformer_rating=rated_array_power,  # match array rating
    )
    return ac_power


@standard_resource_type(R.ac_energy)
def pvradar_ac_energy_from_power(
    ac_power: A[pd.Series, R.ac_power(to_unit='W')],
):
    return convert_power_to_energy_Wh(ac_power, str(R.ac_energy))


@standard_resource_type(R.pv_power)
def pvradar_simple_pv_power(
    ac_power: A[pd.Series, R.ac_power],
) -> pd.Series:
    return ac_power.copy()


@standard_resource_type(R.pv_energy)
def pvradar_pv_energy_from_power(
    pv_power: A[pd.Series, R.pv_power(to_unit='W')],
):
    return convert_power_to_energy_Wh(pv_power, str(R.pv_energy))
