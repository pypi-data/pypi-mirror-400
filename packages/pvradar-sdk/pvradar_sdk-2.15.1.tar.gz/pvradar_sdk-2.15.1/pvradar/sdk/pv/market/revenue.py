from typing import Annotated as A
import pandas as pd

from ...modeling.decorators import resource_type, synchronize_freq
from ...modeling import R
from ...common.pandas_utils import interval_to_index


@resource_type(R.revenue)
@synchronize_freq('lowest')
def pvradar_simple_revenue(
    grid_energy: A[pd.Series, R.grid_energy(to_unit='MWh')],
    electricity_sales_price: A[pd.Series, R.energy_sales_price],  # must be per MWh
) -> pd.Series:
    price_unit = electricity_sales_price.attrs.get('unit', 'USD/MWh')
    currency = price_unit.split('/')[0]
    result = grid_energy * electricity_sales_price
    result.attrs['unit'] = currency
    return result


@resource_type(R.energy_sales_price(set_unit='USD/MWh'))
def pvradar_simple_ppa(
    ppa_price: float,
    interval: pd.Interval,
) -> pd.Series:
    index = interval_to_index(interval, freq='h')
    return pd.Series(ppa_price, index=index)
