# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional


class battery_state_of_charge(ResourceTypeDescriptor):
    """The fraction of a battery’s usable capacity, meaning the portion available for discharge within the allowed operating limits, relative to its rated capacity."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='battery_state_of_charge',
        to_unit='fraction',
        agg='mean',
    )

    def __init__(
        self,
        *,
        to_unit: Annotated[Optional[str], 'convert to unit'] = None,
        set_unit: Annotated[Optional[str], 'override unit'] = None,
        to_freq: Annotated[Optional[str], 'resample result using new freq'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='battery_state_of_charge',
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )
