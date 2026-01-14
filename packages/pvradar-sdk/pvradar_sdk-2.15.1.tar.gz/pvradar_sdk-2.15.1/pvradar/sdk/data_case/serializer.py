from decimal import Decimal
from typing import Any
import pandas as pd
from datetime import datetime, timezone, date

from ..modeling.utils import dtype_to_data_type
from .types import DataCaseScalar, DataCaseSeries, DataCaseTable, DataCase


def series_to_data_case(series: pd.Series, no_index: bool = False) -> DataCaseSeries:
    meta: dict[str, Any] = series.attrs.copy()  # type: ignore
    data_type = dtype_to_data_type(series.dtype.name)

    if data_type == 'object' and len(series) > 0:
        non_na = series.dropna()
        if len(non_na) == 0:
            data_type = 'float'
            series = series.astype('float64')
        else:
            first_non_null = non_na.iloc[0]

            if isinstance(first_non_null, date):
                data_type = 'date'
                series = series.apply(
                    lambda x: int(datetime.combine(x, datetime.min.time(), tzinfo=timezone.utc).timestamp())
                    if pd.notna(x)
                    else x
                )
            elif isinstance(first_non_null, Decimal):
                data_type = 'float'
                series = series.astype('float64')
            elif isinstance(first_non_null, str):
                data_type = 'string'
                # series = series.astype('str')
            elif isinstance(first_non_null, list):
                data_type = 'array'
            else:
                raise ValueError(f'Unsupported object type for data case serialization: {first_non_null.__class__.__name__}')

    if data_type == 'datetime':
        if series.dt.tz:
            meta['tz'] = str(series.dt.tz)
        series = series.astype('int64') // 10**9
        data_type = 'unix_timestamp'
    data = series.to_list()

    # replace NaN with None, because NaN is not JSON serializable
    data = [None if pd.api.types.is_scalar(x) and pd.isna(x) else x for x in data]

    result: DataCaseSeries = {
        'case_type': 'series',
        'data_type': data_type,
        'data': data,
        'name': str(series.name) if series.name else '',
        'meta': meta,
    }

    if not no_index:
        if isinstance(series.index, pd.DatetimeIndex):
            result['index'] = (series.index.astype('int64') // 10**9).to_list()
            new_meta = dict(result['meta'])
            new_meta['index_type'] = 'unix_timestamp'
            if series.index.tz:
                new_meta['tz'] = str(series.index.tz)
            if series.index.freq:
                new_meta['freq'] = series.index.freq.freqstr
            result['meta'] = new_meta

    return result


def df_to_data_case(df: pd.DataFrame) -> DataCaseTable:
    meta = dict(df.attrs.copy())  # type: ignore
    columns: list[DataCaseSeries] = []
    for column in df.columns:
        columns.append(series_to_data_case(df[column], no_index=True))
    if isinstance(df.index, pd.DatetimeIndex):
        index_column = series_to_data_case(pd.Series(df.index, name='((index))'))
        if df.index.freq:
            meta['freq'] = str(df.index.freq.freqstr)  # type: ignore
        columns.append(index_column)
    result: DataCaseTable = {
        'case_type': 'table',
        'columns': columns,
        'meta': meta,  # type: ignore
    }
    return result


def scalar_to_data_case(value: Any) -> DataCaseScalar:
    case_type = 'any'
    if isinstance(value, int):
        case_type = 'int'
    elif isinstance(value, float):
        case_type = 'float'
    elif isinstance(value, str):
        case_type = 'string'
    elif isinstance(value, dict):
        case_type = 'dict'
    return {
        'case_type': case_type,
        'data': value,
        'meta': {},
    }


def check_is_data_case_serializable(subject: Any) -> bool:
    if isinstance(subject, (pd.DataFrame, pd.Series, int, float, str, dict)):
        return True
    return False


def any_to_data_case(subject: Any) -> DataCase:
    if isinstance(subject, pd.DataFrame):
        return df_to_data_case(subject)
    elif isinstance(subject, pd.Series):
        return series_to_data_case(subject)
    elif isinstance(subject, (int, float, str, dict)):
        return scalar_to_data_case(subject)
    else:
        raise ValueError(f'Unsupported type for data case serialization: {type(subject)}')
