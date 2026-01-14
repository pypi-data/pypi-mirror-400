from typing import Iterable, Literal, Optional
import pandas as pd
from ..common.common_utils import check_package_installed
from ..modeling.utils import aggregate_table
from ..client.engine.step_table_types import AbstractStepTable, WaterfallItem, WaterfallMeasure

_dpi = 92  # DPI for converting inches to pixels
_default_figsize = (None, 4)  # in inches


def _ensure_waterfall_items(data: pd.DataFrame | list[WaterfallItem]) -> list[WaterfallItem]:
    if isinstance(data, pd.DataFrame):
        if isinstance(data, AbstractStepTable):
            data = data.to_waterfall_items()
        else:
            collapsed = aggregate_table(data)
            result: list[WaterfallItem] = []
            for col_index, col in enumerate(collapsed.columns):
                value = collapsed[col].iloc[0]
                measure = 'initial' if col_index == 0 else 'relative'
                result.append({'key': str(col), 'value': value, 'measure': measure})
            data = result

    assert isinstance(data, Iterable)
    return data


def _render_plotly_waterfall(
    data: pd.DataFrame | list[WaterfallItem],
    title: str = '',
    add_percentages: bool = True,
    figsize: tuple[float | None, float | None] = _default_figsize,
):
    from plotly import graph_objects as go

    data = _ensure_waterfall_items(data)

    keys: list[str] = []
    values: list[float | int] = []
    measures: list[WaterfallMeasure] = []

    unit = None

    for item in data:
        keys.append(item['key'])
        values.append(item['value'])
        measures.append(item.get('measure', 'absolute'))
        if 'unit' in item:
            if unit is None:
                unit = item['unit']
            elif unit != item['unit']:
                raise ValueError(f'Inconsistent units in waterfall items {unit} vs {item["unit"]}')

    base = values[0]
    pct = [(v / base) * 100 for v in values]

    additional_options = {}
    if add_percentages:
        pct = [(v / base) * 100 for v in values]
        additional_options['customdata'] = pct
        additional_options['hovertemplate'] = '%{x}<br>%{y:.2f} (%{customdata:.2f}%)<extra></extra>'

    fig = go.Figure(
        go.Waterfall(
            name='',
            orientation='v',
            x=keys,
            y=values,
            measure=measures,
            connector={'line': {'width': 1}},
            **additional_options,
        )
    )
    if title:
        fig.update_layout(title=title)

    fig_width = None if figsize[0] is None else figsize[0] * _dpi
    fig_height = None if figsize[1] is None else figsize[1] * _dpi
    margin_top = 10
    if title:
        margin_top += 30
    fig.update_layout(
        width=fig_width,
        height=fig_height,
        margin={
            'l': 10,
            'r': 10,
            't': margin_top,
            'b': 10,
        },
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey', ticksuffix=f' {unit}' if unit else ''),
    )

    return fig


def display_waterfall(
    data: pd.DataFrame | list[WaterfallItem],
    figsize: Optional[tuple[float | None, float | None]] = None,
    title: str = '',
    add_percentages: bool = True,
    renderer: Optional[Literal['plotly', 'kaleido']] = None,
):
    if figsize is None:
        figsize = _default_figsize
    if renderer is None:
        renderer = 'plotly'

    if not check_package_installed('IPython'):
        raise ImportError('IPython package is not installed, while displaying waterfall chart')

    from IPython.display import Image, display  # pyright: ignore [reportMissingImports]

    fig = _render_plotly_waterfall(data, title=title, add_percentages=add_percentages, figsize=figsize)

    if renderer == 'plotly':
        display(fig)
    elif renderer == 'kaleido':
        if not check_package_installed('kaleido'):
            raise ImportError("kaleido/plotly package is not installed. Install it using: pip install 'pvradar-sdk[kaleido]'")

        fig_width = None if figsize[0] is None else figsize[0] * _dpi
        fig_height = None if figsize[1] is None else figsize[1] * _dpi

        display(
            Image(
                fig.to_image(
                    format='png',
                    width=fig_width,
                    height=fig_height,
                ),
                width=fig_width,
            )
        )
