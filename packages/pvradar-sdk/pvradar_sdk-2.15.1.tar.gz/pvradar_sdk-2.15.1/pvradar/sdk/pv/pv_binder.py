from typing import Any, Optional, override

from .design.design import (
    RigidDesign,
    ArrayDesign,
    ModuleDesign,
    StructureDesign,
    FixedStructureDesign,
    TrackerStructureDesign,
    TransformerDesign,
    InverterDesign,
    GridDesign,
)
from .design.component_graph import ComponentGraph
from ..modeling.geo_located_model_context import GeoLocatedModelContext
from ..modeling.basics import BindingNotFound, ModelParam
from ..modeling.model_context import ModelContext
from ..modeling.model_wrapper import ModelBinding
from ..modeling.model_binder import AbstractBinder
from .irradiance import pvlib_irradiance_perez_driesse

_known_properties = [
    'array',
    'module',
    'structure',
]

_design_types = (
    RigidDesign,
    ArrayDesign,
    ModuleDesign,
    StructureDesign,
    FixedStructureDesign,
    TrackerStructureDesign,
    TransformerDesign,
    InverterDesign,
)


class PvBinder(AbstractBinder):
    @override
    def bind(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> Any:
        assert isinstance(context, GeoLocatedModelContext), (
            f'PvBinder requires a GeoLocatedModelContext, got {context.__class__.__name__}'
        )
        if resource_name in _known_properties:
            return getattr(context, resource_name)

        if resource_name == 'sky_diffuse_poa_on_front':
            if not context:
                return BindingNotFound
            model = context.wrap_model(pvlib_irradiance_perez_driesse)
            return ModelBinding(model=model, defaults=defaults or {})
        if as_param and as_param.type:
            if as_param.type in _design_types:
                assert hasattr(context, 'design'), (
                    f'PV design required in model context, but {context.__class__.__name__} does not have it'
                )
            if as_param.type == RigidDesign or as_param.type == ComponentGraph:
                return getattr(context, 'design')
            elif as_param.type == ArrayDesign:
                return getattr(context, 'design').component(component_type='array')
            elif as_param.type == ModuleDesign:
                return getattr(context, 'design').component(component_type='module')
            elif as_param.type == GridDesign:
                return getattr(context, 'design').component(component_type='grid')
            elif as_param.type in (StructureDesign, FixedStructureDesign, TrackerStructureDesign):
                result = getattr(context, 'design').component(component_type='structure')
                if as_param.type == FixedStructureDesign:
                    assert isinstance(result, FixedStructureDesign), (
                        f'expected FixedStructureDesign, got {result.__class__.__name__}'
                    )
                elif as_param.type == TrackerStructureDesign:
                    assert isinstance(result, TrackerStructureDesign), (
                        f'expected TrackerStructureDesign, got {result.__class__.__name__}'
                    )
                return result
            elif as_param.type == TransformerDesign:
                return getattr(context, 'design').component(component_type='transformer')
            elif as_param.type == InverterDesign:
                return getattr(context, 'design').component(component_type='inverter')
        if as_param and as_param.attrs:
            attrs = as_param.attrs
            if attrs.get('resource_type') == 'design':
                return getattr(context, 'design')
        return BindingNotFound
