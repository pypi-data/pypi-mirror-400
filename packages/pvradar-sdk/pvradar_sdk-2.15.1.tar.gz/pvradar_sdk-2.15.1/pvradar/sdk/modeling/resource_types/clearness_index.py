# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional


class clearness_index(ResourceTypeDescriptor):
    """The ratio of the global horizontal irradiance measured at the surface and the extraterrestrial solar radiation at the top of the atmosphere represents how much sunlight penetrates the atmosphere."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='clearness_index',
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
            resource_type='clearness_index',
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )
