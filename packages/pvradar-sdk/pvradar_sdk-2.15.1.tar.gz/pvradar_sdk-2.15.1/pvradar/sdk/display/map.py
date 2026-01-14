import numbers
import random
from typing import Any, Iterable, Literal, Optional, SupportsFloat, cast
from pvlib.location import Location
import pandas as pd
import numpy as np

from ..common.common_utils import check_package_installed
from ..common.logging import log_package_missing
from ..common.constants import COLOR_GREY, COLOR_PRIMARY, COLOR_SECONDARY


MapRenderer = Literal['folium']


def make_branca_colormap(
    color_scale: str | list,
    vmin: SupportsFloat,
    vmax: SupportsFloat,
) -> 'branca.colormap.ColorMap':  # type: ignore  # noqa: F821
    """
    Create a branca colormap from a string or list of colors.
    Args:
        color_scale: Either a string representing a predefined colormap in branca,
                        or a list of colors (as hex strings or RGB tuples), or
                        a list of tuples (position<0..1>, color) similar to matplotlib LinearSegmentedColormap
    """
    import branca.colormap as cm  # pyright: ignore [reportMissingImports]

    if isinstance(color_scale, str):
        # if it's a known color scheme...
        if hasattr(cm.linear, color_scale):
            return getattr(cm.linear, color_scale).scale(float(vmin), float(vmax))
        else:
            # else assume it's a single color
            return cm.LinearColormap(colors=[color_scale, color_scale], vmin=float(vmin), vmax=float(vmax))
    elif isinstance(color_scale, list):
        if not len(color_scale):
            raise ValueError('color_scale list must contain at least one entry')
        first = color_scale[0]
        if isinstance(first, str):
            return cm.LinearColormap(colors=color_scale, vmin=float(vmin), vmax=float(vmax))
        elif isinstance(first, tuple):
            span = float(vmax) - float(vmin)
            positions = [(float(vmin) + float(pos) * span) for pos, color in color_scale]
            colors = [color for pos, color in color_scale]
            return cm.LinearColormap(colors=colors, index=positions, vmin=float(vmin), vmax=float(vmax))
        else:
            raise ValueError(f'color_scale list entries must be either color strings or (position, color). got {type(first)}')
    else:
        raise ValueError(f'color_scale must be either a string or a list of colors, got {type(color_scale)}')


def make_contrast_colors(n: int):
    colors = [
        '#e6194B',
        COLOR_SECONDARY,
        '#4363d8',
        '#f58231',
        '#911eb4',
        '#46f0f0',
        '#f032e6',
        '#bcf60c',
        '#fabebe',
        '#008085',
        '#e6beff',
        '#9A6324',
        '#aaffc3',
        '#000075',
        '#808000',
        '#ffd8b1',
        COLOR_PRIMARY,
    ]
    res = []
    for i in range(n):
        res.append(colors[i % len(colors)])
    return res


def display_map(
    table: Optional[pd.DataFrame] = None,
    *,
    center: Location | tuple[float, float] | None = None,
    center_tooltip: str | None = None,
    color_by: str | Iterable | None = None,
    color_scale: str | list | None = None,
    size_by: str | Iterable | None = None,
    autofit: bool = True,
    legend: bool = True,
    renderer: MapRenderer = 'folium',
    figsize: Optional[tuple[Any, Any]] = None,  # in inches - (12, 5), or in CSS notation ('100%', '300px')
) -> None:
    """
    Args:
        table: A pandas DataFrame containing at least 'latitude' and 'longitude' columns.
        center: A Location object or (latitude, longitude) tuple to center the map on.
        center_tooltip: Tooltip text for the center marker.
        color_by: Column name or iterable to color the markers by
        color_scale:  Either a string representing a predefined colormap in branca,
                        or a list of colors (as hex strings or RGB tuples), or
                        a list of tuples (position<0..1>, color) similar to matplotlib LinearSegmentedColormap
        size_by: Column name or iterable to size the markers by
        autofit: Whether to autofit the map to the markers on display
        renderer: Map rendering library to use. Currently only 'folium' is supported.
        figsize: Size of the map to render. Either in inches for compatibility with matplotlib (e.g., (12, 5))

    Examples:
        >>> display_map(df, color_scale='plasma')
        >>> display_map(df, color_by='soiling', color_scale=['green', '#ff0000'])
        >>> display_map(df, color_by=df['soiling'] + df['snow'], color_scale=[(0, 'red'), (0.2, 'yellow'), (1, 'green')], size_by='capacity')
    """
    from IPython.display import display  # pyright: ignore [reportMissingImports]

    map = render_map(
        table,
        center=center,
        center_tooltip=center_tooltip,
        color_by=color_by,
        color_scale=color_scale,
        size_by=size_by,
        autofit=autofit,
        legend=legend,
        renderer=renderer,
        figsize=figsize,
    )

    display(map)


def render_map(
    table: Optional[pd.DataFrame] = None,
    *,
    center: Location | tuple[float, float] | None = None,
    center_tooltip: str | None = None,
    color_by: str | Iterable | None = None,
    color_scale: str | list | None = None,
    size_by: str | Iterable | None = None,
    legend: bool = True,
    autofit: bool = True,
    renderer: MapRenderer = 'folium',
    figsize: Optional[tuple[Any, Any]] = None,  # in inches - (12, 5), or in CSS notation ('100%', '300px')
):
    def _is_notna_scalar(x):
        try:
            return np.isscalar(x) and pd.notna(x)  # pyright: ignore
        except Exception:
            return False

    if table is None:
        table = pd.DataFrame(columns=['latitude', 'longitude'])

    if not check_package_installed('branca'):
        log_package_missing('branca', 'folium maps')
        return None

    if color_scale is None:
        color_scale = [COLOR_SECONDARY, '#0000ff']  # corresponds to matplotlib winter_r (more or less)

    if not check_package_installed(renderer):
        raise ImportError(f'{renderer} package is not installed. Please install it to use display_map feature')

    import folium  # pyright: ignore [reportMissingImports]

    explicit_center = None
    if isinstance(center, Location):
        explicit_center = (center.latitude, center.longitude)
    elif isinstance(center, tuple):
        explicit_center = center

    if explicit_center:
        map_center = explicit_center
    elif table is not None and len(table) > 0:
        map_center = (table['latitude'].mean(), table['longitude'].mean())
    else:
        map_center = (51.47795, 0)  # Greenwich, UK

    DPI = 92  # dots per inch
    if figsize is None:
        figsize = ('100%', '400px')
    map_width = figsize[0] if isinstance(figsize[0], str) else figsize[0] * DPI
    map_height = figsize[1] if isinstance(figsize[1], str) else figsize[1] * DPI

    m = folium.Map(
        location=map_center,
        zoom_start=6,
        width=map_width,
        height=map_height,
        fname=f'tmp_map_{random.randint(0, 10_000_000)}.html',
    )

    if explicit_center is not None:
        folium.Marker(
            location=explicit_center,
            icon=folium.Icon(color='red'),
            tooltip=center_tooltip or 'Center',
        ).add_to(m)

    counter = 0

    fg = folium.FeatureGroup(name='Markers')

    assert {'latitude', 'longitude'}.issubset(table.columns), "Table must contain 'latitude' and 'longitude' columns"

    color_caption = None
    if isinstance(color_by, str):
        assert color_by in table.columns, f"Column '{color_by}' not found in table."
        color_caption = color_by
        color_by = table[color_by]  # type: ignore

    if color_by is not None:
        color_by_values = list(color_by)
        # first non-NaN and non-null value
        first_val = next((val for val in color_by_values if _is_notna_scalar(val)), None)
        if isinstance(first_val, numbers.Number) or isinstance(first_val, np.number):
            numeric_vals = cast(list[float], color_by_values)
            vmin = min(numeric_vals)
            vmax = max(numeric_vals)
            colormap = make_branca_colormap(color_scale, vmin=vmin, vmax=vmax)

            if color_caption:
                colormap.caption = color_caption

            if legend:
                colormap.add_to(m)

            colors = [COLOR_GREY if pd.isna(value) else colormap(value) for value in numeric_vals]
        elif isinstance(first_val, str):
            color_by_values = list(color_by)
            unique_values = pd.Series(color_by_values).dropna().unique()
            unique_colors = make_contrast_colors(len(unique_values))
            colors = []
            for i, val in enumerate(color_by_values):
                pos = next((idx for idx, v in enumerate(unique_values) if v == val), None)
                colors.append(unique_colors[pos] if pos is not None else COLOR_GREY)
        else:
            colors = COLOR_GREY * len(table)
    else:
        colors = [COLOR_SECONDARY] * len(table)

    if size_by is not None:
        if isinstance(size_by, str):
            size_by = table[size_by]  # type: ignore
        all_size_values = list(size_by)
        vmin = min(all_size_values)
        vmax = max(all_size_values)
        norm_sizes = (np.array(all_size_values) - vmin) / (vmax - vmin)
        sizes = [8 if pd.isna(s) else s * 10 + 5 for s in norm_sizes]  # Scale size between 5 and 15
    else:
        sizes = [8] * len(table)

    for i, row in table.iterrows():
        # iterate over the DataFrame columns and create a popup for each marker
        # based on all columns

        popup_text = '<br>'.join(f'{col}: {row[col]}' for col in table.columns if _is_notna_scalar(row[col]))
        popup_text = f'<b>{i}</b><br>{popup_text}'

        marker = folium.CircleMarker(
            location=(row['latitude'], row['longitude']),
            radius=sizes[counter],
            color=colors[counter],
            fill=True,
            fill_color=colors[counter],
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=str(i),
        )
        marker.add_to(fg)
        marker.add_to(m)
        counter += 1

    if autofit and len(table) > 1:
        bounds = fg.get_bounds()
        if bounds:
            m.fit_bounds(bounds)  # type: ignore

    f = folium.Figure(width=map_width, height=map_height)
    m.add_to(f)
    return m


class GeoLocatedDataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return GeoLocatedDataFrame

    def display_map(
        self,
        center_tooltip: str | None = None,
        color_by: str | None = None,
        size_by: str | None = None,
        autofit: bool = True,
        figsize: Optional[tuple[Any, Any]] = None,
    ):
        return display_map(
            self,
            center=self.attrs.get('location'),
            center_tooltip=center_tooltip,
            color_by=color_by,
            size_by=size_by,
            autofit=autofit,
            figsize=figsize,
        )
