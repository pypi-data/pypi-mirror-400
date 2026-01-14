import numpy as np
import csv
from io import StringIO
import re
from typing import Any, Literal, TypeGuard, TypeVar, Annotated, TypedDict, Optional
from pandas import DataFrame, DatetimeIndex, Series, Interval, Timestamp, date_range, read_csv, to_datetime
from dataclasses import dataclass
import pandas as pd
from pandas.tseries.frequencies import to_offset
from pydantic import Field

SeriesOrFrame = TypeVar('SeriesOrFrame', Series, DataFrame)
SeriesOrNdarray = TypeVar('SeriesOrNdarray', Series, np.ndarray)
TimestampAlignment = Literal['left', 'center', 'right']
EPSILON = pd.Timedelta('1ns')


def is_series_or_frame(obj: object) -> TypeGuard[SeriesOrFrame]:
    return isinstance(obj, Series) or isinstance(obj, DataFrame)


@dataclass
class UnitConversion:
    suffix: str
    factor: float


field_map = {
    'distance': UnitConversion('km', 1e-3),
}

exclude_rounding = ['lat', 'lon']


def safe_copy(df: SeriesOrFrame) -> SeriesOrFrame:
    if isinstance(df, pd.Series):
        return df.copy()
    if isinstance(df, pd.DataFrame):
        result = df._constructor() if hasattr(df, '_constructor') else pd.DataFrame()  # pyright: ignore[reportCallIssue]
        for col in df.columns:
            result[col] = df[col].copy()
        copy_df_attrs(df, result)
        return result  # type: ignore
    raise ValueError(f'Unsupported type for safe_copy: {type(df)}')


def copy_df_attrs(from_df: pd.DataFrame, to_df: pd.DataFrame) -> None:
    to_df.attrs = from_df.attrs.copy()
    for col in from_df.columns:
        to_df[col].attrs = from_df[col].attrs.copy()


def process_df(df: DataFrame, precise: bool = False, convert_units: bool = True) -> DataFrame:
    copy_made = False
    if convert_units:
        df = df.copy(deep=True)
        copy_made = True
        for key in field_map.keys():
            if key in df.columns:
                new_key = key + '_' + field_map[key].suffix
                df[new_key] = df[key] * field_map[key].factor
                df.drop(columns=[key], inplace=True)

    if not precise:
        if not copy_made:
            df = df.copy(deep=True)
        float_columns = df.select_dtypes(include='float').columns
        columns_to_round = [col for col in float_columns if col not in exclude_rounding]
        df[columns_to_round] = df[columns_to_round].round(2)
    return df


def api_csv_string_to_df(csv_str: str, tz: str | None = None) -> DataFrame:
    if csv_str.strip() == '':
        # Return empty DataFrame if the CSV string is empty
        return DataFrame()
    header = next(csv.reader(StringIO(csv_str)))
    df = read_csv(StringIO(csv_str))

    if header[0] in ['isoDate', 'iso_date']:
        iso_date = to_datetime(df[header[0]])
        if iso_date.dt.tz is None:
            # ATTENTION: quickfix, unclear why we need it
            iso_date = iso_date.dt.tz_localize('UTC')
        try:
            df[header[0]] = iso_date if tz is None else iso_date.dt.tz_convert(tz)
        except Exception as e:
            raise RuntimeError(f'Error converting date to timezone: {e}')
        index_name = header[0]
        if 'forecast_hour' in df.columns:
            index_name = [index_name, 'forecast_hour']
        df.set_index(index_name, inplace=True)
        maybe_adjust_index_freq(df)

    if header[0] == 'month' and len(df) == 12:
        df.set_index(header[0], inplace=True)
    return df


def get_anchor(timestamp: pd.Timestamp) -> pd.Timestamp:
    """
    anchor: midnight (start of the day) of the first timestamp.
    """
    return timestamp.normalize()


def get_period(
    subject: SeriesOrFrame | pd.Timestamp | pd.DatetimeIndex | None = None,
    *,
    freq: Optional[str] = None,
) -> pd.Timedelta:
    if freq is not None:
        return freq_to_timedelta(freq)

    assert subject is not None, 'provide either `freq` or `resource`'

    if is_series_or_frame(subject):
        f = infer_freq_and_validate(subject)
        return freq_to_timedelta(f)

    if isinstance(subject, pd.DatetimeIndex):
        assert len(subject) > 1, 'DatetimeIndex must have at least 2 timestamps'
        period = subject[1] - subject[0]
        if len(subject) > 2:
            deltas = subject[1:] - subject[:-1]
            assert (deltas == period).all(), 'DatetimeIndex must be regular (constant period)'
        return period

    raise ValueError('get_period(subject=Timestamp) requires `freq`')


def get_offset(
    resource: SeriesOrFrame | pd.Timestamp,
    period: Optional[pd.Timedelta] = None,
) -> pd.Timedelta:
    """
    offset = (first timestamp - midnight of its day) modulo period
    """
    if period is None:
        if not is_series_or_frame(resource):
            raise TypeError('when auto-detecting period, resource must be a Series or DataFrame')
        freq = infer_freq_and_validate(resource)
        period = freq_to_timedelta(freq)

    if is_series_or_frame(resource):
        if resource.empty:
            raise ValueError('Cannot get offset for an empty resource')
        timestamp = resource.index[0]
    else:
        timestamp = resource

    assert isinstance(timestamp, pd.Timestamp), f'pd.Timestamp expected, got {type(timestamp)}'
    anchor = get_anchor(timestamp)
    return (timestamp - anchor) % period


def get_phase(
    resource: SeriesOrFrame | pd.Timestamp,
    *,
    period: Optional[pd.Timedelta] = None,
    freq: Optional[str] = None,
) -> float:
    """
    Grid phase in [0,1): measured at the LEFT edge of the period.
    If labels are not left-aligned (e.g., center), we subtract the alignment shift first.
    """
    if period is None:
        period = freq_to_timedelta(freq) if freq is not None else get_period(resource)

    # label-based offset → left-edge offset
    label_offset = get_offset(resource, period=period)
    grid_offset = label_offset % period

    return grid_offset / period


def _make_effective_boundary(interval: Interval) -> tuple[pd.Timestamp, pd.Timestamp]:
    effective_left = interval.left
    effective_right = interval.right
    if interval.closed == 'neither' or interval.closed == 'right':
        effective_left += EPSILON
    if interval.closed == 'neither' or interval.closed == 'left':
        effective_right -= EPSILON
    return (effective_left, effective_right)


def crop_by_interval(df: SeriesOrFrame, interval: Interval) -> SeriesOrFrame:
    assert isinstance(interval, Interval)
    assert isinstance(interval.left, Timestamp)
    assert isinstance(interval.right, Timestamp)

    effective_left, effective_right = _make_effective_boundary(interval)

    try:
        result = df.loc[effective_left:effective_right]
    except KeyError:
        # fallback for non-monotonic index
        idx = df.index
        mask = (idx >= effective_left) & (idx <= effective_right)
        result = df.loc[mask]

    if isinstance(df, Series):
        return result

    if isinstance(df, DataFrame):
        # workaround for bug in pandas overwriting attrs
        for column in df.columns:
            result[column].attrs = df[column].attrs
        return result
    raise ValueError(f'crop_by_interval supports only Series or DataFrame, got {type(df)}')


def pad_to_interval(
    obj: SeriesOrFrame,
    interval: pd.Interval,
    *,
    pad_value: Literal['fill'] | float = 0,
    freq: Optional[str] = None,
) -> SeriesOrFrame:
    """adds a value on the left and/or right edge if the interval exceeds the object's index range"""
    if not isinstance(interval, pd.Interval):
        raise TypeError('interval must be a pd.Interval')
    if pad_value != 'fill' and not isinstance(pad_value, (int, float)):
        raise TypeError("pad_value must be 'fill' or a number")

    idx_min = obj.index.min()
    idx_max = obj.index.max()
    left = interval.left
    right = interval.right

    if freq is None and 'freq' in obj.attrs:
        freq = str(obj.attrs['freq'])

    if freq is not None:
        left = pd.Timestamp(left).ceil(freq)
        right = pd.Timestamp(right).floor(freq)

    def make_pad(val, pos):
        if isinstance(obj, pd.DataFrame):
            if pad_value == 'fill':
                fill_val = obj.iloc[0] if pos == 'left' else obj.iloc[-1]
                return pd.DataFrame([fill_val], index=[val])
            return pd.DataFrame([[pad_value] * len(obj.columns)], index=[val], columns=obj.columns)
        else:
            if pad_value == 'fill':
                fill_val = obj.iloc[0] if pos == 'left' else obj.iloc[-1]
                return pd.Series(fill_val, index=[val])
            return pd.Series(pad_value, index=[val])

    original = obj
    if left < idx_min:
        if isinstance(obj, pd.DataFrame) and obj is original:
            obj = safe_copy(obj)
        obj = pd.concat([make_pad(left, 'left'), obj])  # pyright: ignore[reportAssignmentType]
    if right > idx_max:
        if isinstance(obj, pd.DataFrame) and obj is original:
            obj = safe_copy(obj)

        obj = pd.concat([obj, make_pad(right, 'right')])  # pyright: ignore[reportAssignmentType]

    if obj is not original:
        if isinstance(original, pd.DataFrame):
            copy_df_attrs(original, obj)  # pyright: ignore[reportArgumentType]
        else:
            obj.attrs = original.attrs.copy()
    return obj  # pyright: ignore[reportReturnType]


def interval_to_index(interval: Interval, freq: str = '1h') -> DatetimeIndex:
    effective_left, effective_right = _make_effective_boundary(interval)
    return date_range(start=effective_left, end=effective_right, freq=freq)


def interval_duration_years(interval: Interval) -> float:
    return (interval.right - interval.left) / pd.Timedelta(days=365.25)


_acceptable_period_formats = ' or '.join(['YYYY', 'YYYY-MM-DD', 'YYYY..YYYY', 'YYYY-MM-DD..YYYY-MM-DD']) + ' (all inclusive)'

PeriodField = Annotated[
    str,
    Field(
        description=f'{_acceptable_period_formats}',
        examples=['Interval in ISO 8601', '2020', '2020-01-01', '2020..2020', '2020-01-01..2020-12-31'],
    ),
]


class ParsedTimestamp(TypedDict):
    timestamp: pd.Timestamp
    type: Literal['year', 'date', 'datetime']


def parse_timestamp_str(s: str) -> ParsedTimestamp:
    if re.match(r'^\d{4}$', s):
        return {'timestamp': pd.Timestamp(f'{s}-01-01'), 'type': 'year'}
    elif re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return {'timestamp': pd.Timestamp(s), 'type': 'date'}
    elif re.match(r'^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})?$', s):
        return {'timestamp': pd.Timestamp(s), 'type': 'datetime'}
    else:
        raise ValueError(
            f'Invalid timestamp format "{s}". Acceptable formats: "YYYY", "YYYY-MM-DD", "YYYY-MM-DDTHH:MM:SS[Z|±HH:MM]"'
        )


# copied from implementation in outlet
# see unit tests for examples
def period_str_to_date_tuple(period: PeriodField, *, closed_left=True, closed_right=True) -> tuple[str, str]:
    if period.isnumeric():
        if len(period) != 4:
            raise ValueError(f'Invalid period format "{period}". Acceptable formats: {_acceptable_period_formats}')
        return f'{period}-01-01', f'{period}-12-31'
    elif '..' in period:
        # TODO: check that start <= end
        start, end = period.split('..')
        if start.isnumeric() and end.isnumeric():
            if len(start) != 4 or len(end) != 4:
                raise ValueError(f'Invalid period format "{period}". Acceptable formats: {_acceptable_period_formats}')
            if not closed_left or not closed_right:
                raise ValueError('Non-closed intervals are only supported for date periods, not years')
            return f'{start}-01-01', f'{end}-12-31'
        elif re.match(r'\d{4}-\d{2}-\d{2}', start) and re.match(r'\d{4}-\d{2}-\d{2}', end):
            # TODO: check that month/date make sense, e.g. 2020-02-30 is invalid
            if not closed_left:
                start = (pd.Timestamp(start) + pd.Timedelta(1, 'd')).strftime('%Y-%m-%d')
            if not closed_right:
                end = (pd.Timestamp(end) - pd.Timedelta(1, 'd')).strftime('%Y-%m-%d')
            return start, end
    elif re.match(r'\d{4}-\d{2}-\d{2}', period):
        return period, period
    raise ValueError(f'Invalid period format "{period}". Acceptable formats: {_acceptable_period_formats}')


def period_str_to_interval(period: PeriodField) -> Interval:
    closed_left = True
    closed_right = True

    if period.startswith('['):
        period = period[1:]
    if period.startswith('('):
        period = period[1:]
        closed_left = False
    if period.endswith(']'):
        period = period[:-1]
    if period.endswith(')'):
        period = period[:-1]
        closed_right = False

    if '/' in period:
        # process according to ISO 8601
        chunks = period.split('/')
        if len(chunks) != 2:
            raise ValueError(f'Invalid period format "{period}". Acceptable formats: {_acceptable_period_formats}')
        start = parse_timestamp_str(chunks[0])

        end = parse_timestamp_str(chunks[1])
        if end['type'] == 'year':
            end['timestamp'] = pd.Timestamp(f'{end["timestamp"].year}-12-31T23:59:59', tz=end['timestamp'].tz)
        elif end['type'] == 'date':
            end_str = f'{end["timestamp"].year}-{end["timestamp"].month:02d}-{end["timestamp"].day:02d}T23:59:59'
            end['timestamp'] = pd.Timestamp(end_str, tz=end['timestamp'].tz)
        left = Timestamp(start['timestamp'])
        right = Timestamp(end['timestamp'])
    else:
        date_tuple = period_str_to_date_tuple(period, closed_left=closed_left, closed_right=closed_right)

        left = Timestamp(date_tuple[0])
        right = Timestamp(date_tuple[1] + 'T23:59:59')

    return Interval(left=left, right=right, closed='both')


def series_list_to_dataframe(series_list: list[Series], *, filter: Any = None) -> DataFrame:
    result = DataFrame({s.name: s for s in series_list})
    result.index = series_list[0].index

    if filter is not None:
        if callable(filter):
            filter = filter(result)
        result = result[filter]

    # workaround for bug in pandas overwriting attrs
    for series in series_list:
        result[series.name].attrs = series.attrs
    return result


def normalize_freq_str(freq: str) -> str:
    return re.sub(r'^1([^0-9])', r'\1', freq)


def infer_freq_as_str(series: pd.Series | pd.DataFrame | pd.DatetimeIndex) -> str | None:
    """infers h, 2h, 3h ..., D, 2D, 3D ..., MS, YS"""
    if is_series_or_frame(series):
        index = series.index
    else:
        index = series
    assert isinstance(index, pd.DatetimeIndex), f'infer_freq() only supports series with datetime index, got {type(index)}'
    if index.freq:
        return index.freq.freqstr
    if len(series) > 1:
        first = index[0]
        second = index[1]
        td = pd.to_timedelta(second - first)
        if first.year != second.year and first.month == 1 and first.day == 1 and first.hour == 0:
            attempted = date_range(start=first, periods=len(index), freq='YS')
            if attempted.equals(index):
                return 'YS'
        if first.month != second.month and first.day == second.day and first.hour == 0:
            if first.day == 1:
                attempted = date_range(start=first, periods=len(index), freq='MS')
                if attempted.equals(index):
                    return 'MS'
        if td.days > 0 and first.hour == 0:
            candidate = normalize_freq_str(f'{td.days}D')
            try:
                attempted = date_range(start=first, periods=len(index), freq=candidate)
                if attempted.equals(index):
                    return normalize_freq_str(candidate)
            except Exception:
                # inference failed for unclear reason, but we can ignore it
                return None
        if td.days == 0 and td.components.hours:
            return normalize_freq_str(f'{td.components.hours}h')
        return None
    return None


def min_index_timedelta(s: pd.Series) -> pd.Timedelta:
    i = s.index
    if len(i) < 2:
        return pd.Timedelta(0)
    return (i[1:] - i[:-1]).min()


def infer_freq_and_validate(series: pd.Series | pd.DataFrame | pd.DatetimeIndex) -> str:
    str_freq = infer_freq_as_str(series)
    attr_freq = None
    if is_series_or_frame(series):
        attr_freq = series.attrs.get('freq', None)
    if str_freq is None and attr_freq is None:
        raise ValueError('Cannot infer frequency - no clear freq in index and no freq attr')
    if str_freq is None:
        return str(attr_freq)
    if attr_freq is None:
        return str(str_freq)
    if str_freq != normalize_freq_str(attr_freq):
        raise ValueError(f'Inferred frequency "{str_freq}" does not match frequency attribute "{attr_freq}"')
    return str_freq


def freq_to_timedelta(freq: str) -> pd.Timedelta:
    if not re.match(r'^\d+', freq):
        freq = '1' + freq
    period = pd.Timedelta(freq)
    return period


def maybe_adjust_index_freq(df: SeriesOrFrame | pd.DatetimeIndex) -> None:
    if is_series_or_frame(df):
        index = df.index
        assert isinstance(index, pd.DatetimeIndex), 'maybe_adjust_index_freq() called on non-datetime index'
        actual_freq = index.freq
        if actual_freq:
            # already set, nothing to do
            return
        assumed_freq = df.attrs['freq'] if 'freq' in df.attrs else infer_freq_as_str(df)
        if not assumed_freq:
            # there is no expected freq, so nothing to do
            return
    elif isinstance(df, pd.DatetimeIndex):
        index = df
        assumed_freq = infer_freq_as_str(index)
    else:
        raise ValueError('maybe_adjust_index_freq() called on non-datetime index')

    assert isinstance(assumed_freq, str)

    inferred = infer_freq_as_str(df)
    if inferred:
        new_index = pd.date_range(start=index[0], periods=len(index), freq=assumed_freq)
        if len(new_index) == len(index) and new_index[-1] == index[-1]:
            df.index = new_index


def interval_from_series(series: SeriesOrFrame) -> Interval:
    return pd.Interval(series.index.min(), series.index.max(), closed='both')


def update_attrs_nested(obj: SeriesOrFrame, attrs: dict[str, Any]) -> None:
    obj.attrs.update(attrs)  # pyright: ignore[reportArgumentType, reportCallIssue]
    if isinstance(obj, pd.DataFrame):
        for col in obj.columns:
            if isinstance(obj[col], pd.Series):
                obj[col].attrs.update(attrs)  # pyright: ignore[reportArgumentType, reportCallIssue]


def trim_to_full_years(obj: SeriesOrFrame) -> SeriesOrFrame:
    if not isinstance(obj.index, pd.DatetimeIndex):
        raise TypeError('index must be a DatetimeIndex')
    if obj.empty:
        return obj

    idx = obj.index
    tz = idx.tz
    freqstr = idx.freqstr or pd.infer_freq(idx)
    if not freqstr:
        raise ValueError('DatetimeIndex must have a fixed freq')
    step = to_offset(freqstr)

    first = idx[0]
    last = idx[-1]

    # Left boundary: first Jan 1 at/after the first timestamp (in the same tz)
    left = pd.Timestamp(year=first.year, month=1, day=1, tz=tz)
    if first > left:
        left = pd.Timestamp(year=first.year + 1, month=1, day=1, tz=tz)

    # Right boundary: latest year for which we have the *full* set of periods
    def year_right_edge(y: int) -> pd.Timestamp:
        assert step is not None
        # inclusive right edge for a full year at frequency `step`
        return pd.Timestamp(year=y + 1, month=1, day=1, tz=tz) - step

    y = last.year
    # Walk back until the final year is complete at the given freq
    while y >= left.year and last < year_right_edge(y):
        y -= 1

    if y < left.year:
        # No complete years in the data
        return obj.iloc[0:0]

    right = year_right_edge(y)
    return obj.loc[left:right]


def fillna_edges_only(x: SeriesOrNdarray) -> SeriesOrNdarray:
    is_series = isinstance(x, Series)
    arr = x.values if is_series else np.asarray(x, dtype=float)
    isnan = np.isnan(arr)  # pyright: ignore[reportCallIssue, reportArgumentType]

    valid = ~isnan
    if not np.any(valid):
        filled = np.zeros_like(arr)
    else:
        first_valid = np.argmax(valid)
        last_valid = len(arr) - np.argmax(valid[::-1]) - 1

        if np.any(isnan[first_valid : last_valid + 1]):
            raise ValueError('NaN values found in the middle of the array')

        filled = arr.copy()
        filled[:first_valid] = 0
        filled[last_valid + 1 :] = 0

    if is_series:
        return Series(filled, index=x.index, name=x.name)  # pyright: ignore[reportReturnType]
    return filled  # pyright: ignore[reportReturnType]


def remove_dst(timestamps: list[pd.Timestamp], from_tz: str, to_tz: str) -> list[pd.Timestamp]:
    result: list[pd.Timestamp] = []
    last_dst = None
    zero_delta = pd.Timedelta(0)
    hour_delta = pd.Timedelta(hours=1)
    last_ts = None
    for ts in timestamps:
        if ts.tzinfo is not None:
            raise ValueError('Timestamps must be naive')
        from_localized = ts.tz_localize(from_tz, ambiguous='NaT')
        if from_localized is pd.NaT:
            if last_ts is None or last_dst is None:
                raise ValueError(f'Failed to remove_dst as data starts with ambiguous timestamp during DST transition {ts}')
            ts = ts.tz_localize(to_tz, ambiguous=False)
            if last_dst > zero_delta:
                ts = ts - hour_delta
            if ts <= last_ts:
                ts = ts + hour_delta
        else:
            last_dst = from_localized.dst()
            if last_dst != zero_delta:
                ts = ts - hour_delta
            ts = ts.tz_localize(to_tz)

        last_ts = ts
        result.append(ts)

    return result


def validate_timestamp_interval(value: pd.Interval) -> None:
    if (
        not isinstance(value, pd.Interval)
        or not isinstance(value.left, pd.Timestamp)
        or not isinstance(value.right, pd.Timestamp)
    ):
        raise ValueError('must be an Interval with pd.Timestamp endpoints')
    if value.left > value.right:
        raise ValueError('in interval the left endpoint must be less than or equal to right endpoint')


def interpret_interval(interval: Any) -> pd.Interval:
    """
    interpret incoming parameter as an interval for a context.
    Main conversions: str -> pd.Interval, closed=right -> closed=both
    """
    if isinstance(interval, (int, float)):
        if int(interval) != interval:
            raise ValueError('interval cannot be a float with a non-zero decimal part')
        if interval > 2100 or interval < 1950:
            raise ValueError(f'only years between 1950 and 2100 can be passed as interval, got {interval}')
        interval = str(int(interval))
    if isinstance(interval, str):
        interval = period_str_to_interval(interval)
    if isinstance(interval, pd.Interval) and interval.closed == 'right':
        interval = pd.Interval(interval.left, interval.right, closed='both')
    if not isinstance(interval, pd.Interval):
        raise ValueError(f'type cannot be interpreted as interval: {type(interval)}')
    return interval


def interval_to_str(interval: pd.Interval, *, round_by: str = 'day') -> str:
    return f'{interval.left.strftime("%Y-%m-%d")}/{interval.right.strftime("%Y-%m-%d")}'


def daily_accumulated_to_hourly(series: pd.Series, alignment: TimestampAlignment = 'right', reset_hour=1) -> pd.Series:
    if len(series) < 24:
        raise ValueError(f'daily_accumulated_to_hourly requires at least 24 data points (one day), got {len(series)}')

    if alignment not in ['left', 'right']:
        raise ValueError(
            (
                f'only left/right alignment are supported in daily_accumulated_to_hourly, got {alignment}. '
                'You can realign in a separate step'
            )
        )

    assert isinstance(series.index, pd.DatetimeIndex), 'series must have a DatetimeIndex'
    assert series.index[0].hour == 0, f'series must start at hour 00:00, got hour {series.index[0].hour}'
    assert series.index[-1].hour == 23, f'series must end at hour 23:00, got hour {series.index[-1].hour}'

    hourly_diff = series.diff()  # pyright: ignore
    assert isinstance(hourly_diff.index, pd.DatetimeIndex)
    result = hourly_diff.where(hourly_diff.index.hour != reset_hour, series)

    if alignment == 'left':
        result = pd.Series(
            data=result.tolist()[1:] + [0],
            index=series.index,
            name=series.name,
        )
    elif alignment == 'right':
        # the first value has no previous value to diff against, so we set it to 0 just to avoid wild values
        # we assume that all accumulated values start from 0 and are positive
        result.iloc[0] = 0  # pyright: ignore
    else:
        raise ValueError(
            (
                f'only left/right alignment are supported in daily_accumulated_to_hourly, got {alignment}. '
                'You can realign in a separate step'
            )
        )

    return result
