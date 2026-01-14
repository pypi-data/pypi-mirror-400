from typing import Annotated as A
import pandas as pd
import numpy as np

from ...modeling.basics import LambdaArgument
from ...modeling.decorators import standard_resource_type
from ...modeling.utils import convert_power_to_energy_Wh
from ...modeling import R
from ...common.pandas_utils import interval_to_index
from ..design.design import GridDesign
from ..design.component_graph import ComponentGraph
from ...modeling.model_context import BaseModelContext


@standard_resource_type(R.grid_power, override_unit=True)
def pvradar_simple_grid(
    *,
    pv_power: A[pd.Series, R.pv_power(to_unit='W')],
    interval: pd.Interval,
    grid_limit: A[pd.Series | int | float | None, LambdaArgument(GridDesign, lambda g: g.grid_limit)],
    design: ComponentGraph,
    context: BaseModelContext,
) -> pd.Series:
    has_battery = len(design.find_components(component_type='battery')) > 0

    # performance short circuit: no BESS, no grid limit
    if grid_limit is None and has_battery is None:
        return pv_power

    if has_battery:
        bess_power = context.resource(R.bess_power(to_unit='W'))
        pv_to_bess_power = context.resource(R.pv_to_bess_power(to_unit='W'))
        total_power = pv_power + bess_power - pv_to_bess_power
    else:
        total_power = pv_power

    if grid_limit is None:
        return total_power

    if isinstance(grid_limit, (int, float)):
        index = interval_to_index(interval=interval, freq='1h')
        grid_limit = pd.Series(float(grid_limit), index=index)

    if not isinstance(grid_limit, pd.Series):
        raise TypeError('`grid_limit` must be None, int, float, or pd.Series')

    return pd.Series(np.minimum(total_power.to_numpy(), grid_limit.to_numpy()), index=total_power.index)


@standard_resource_type(R.grid_energy, override_unit=True)
def pvradar_grid_energy_from_power(
    grid_power: A[pd.Series, R.grid_power(to_unit='W')],
):
    return convert_power_to_energy_Wh(grid_power, str(R.grid_energy))
