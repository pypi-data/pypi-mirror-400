import pvlib
from typing import Annotated as A
import pandas as pd
import numpy as np

from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...modeling.basics import LambdaArgument as LA
from ...modeling import ModelContext
from ..design.design import (
    ArrayDesign,
    FixedStructureDesign,
    TrackerStructureDesign,
    StructureDesign,
    ModuleDesign,
    ModuleOrientation,
)


@standard_resource_type(R.collector_shading_fraction, override_unit=True)  # TODO rename to collector_shaded_fraction ??
def pvlib_shaded_fraction1d(
    context: ModelContext,
    solar_zenith: A[pd.Series, R.solar_zenith_angle],
    solar_azimuth: A[pd.Series, R.solar_azimuth_angle],
    collector_width: A[float, LA(StructureDesign, lambda d: d.collector_width)],
    pitch: A[float, LA(ArrayDesign, lambda d: d.pitch)],
    structure: StructureDesign,
    axis_azimuth: A[float, LA(StructureDesign, lambda d: d.axis_azimuth)],
    axis_tilt: A[float, LA(StructureDesign, lambda d: d.axis_tilt)],
    collector_to_axis_offset: A[float, LA(StructureDesign, lambda d: d.collector_to_axis_offset)],
    ground_cross_axis_slope: A[float, LA(ArrayDesign, lambda d: d.ground_cross_axis_slope)],
) -> pd.Series:
    if isinstance(structure, FixedStructureDesign):
        surface_rotation_angle = structure.tilt
    elif isinstance(structure, TrackerStructureDesign):
        surface_rotation_angle = context.resource(R.tracker_rotation_angle)
    else:
        raise ValueError('Structure needs to be either fixed-tilt or tracker.')

    shaded_fraction: pd.Series = pvlib.shading.shaded_fraction1d(
        solar_zenith=solar_zenith,
        solar_azimuth=solar_azimuth,
        axis_azimuth=axis_azimuth,
        shaded_row_rotation=surface_rotation_angle,
        shading_row_rotation=surface_rotation_angle,
        collector_width=collector_width,
        pitch=pitch,
        axis_tilt=axis_tilt,  # type: ignore
        surface_to_axis_offset=collector_to_axis_offset,  # type: ignore
        cross_axis_slope=ground_cross_axis_slope,  # type: ignore
    )
    shaded_fraction[shaded_fraction < 0.01] = 0  # remove very small values belos 1%
    return shaded_fraction


@standard_resource_type(R.shading_loss_factor, override_unit=True)
def pvradar_shading_loss_factor(
    shaded_fraction: A[pd.Series, R.collector_shading_fraction],
    module_orientation: A[ModuleOrientation, LA(StructureDesign, lambda d: d.module_orientation)],
    num_mod_cross_section: A[int, LA(StructureDesign, lambda d: d.number_modules_cross_section)],
    cell_string_count: A[int, LA(ModuleDesign, lambda d: d.cell_string_count)],
    is_half_cell: A[bool, LA(ModuleDesign, lambda d: d.half_cell)],
) -> pd.Series:
    if module_orientation == 'horizontal':
        total_blocks = cell_string_count * num_mod_cross_section
    else:
        if is_half_cell:
            # half cell: module separated in two parts along long side
            total_blocks = num_mod_cross_section * 2
        else:
            total_blocks = num_mod_cross_section
    shaded_blocks = np.ceil(total_blocks * shaded_fraction)
    shading_loss_fraction = pd.Series(shaded_blocks / total_blocks, index=shaded_fraction.index)
    return shading_loss_fraction
