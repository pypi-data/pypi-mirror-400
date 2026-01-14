from typing import Optional, override
from .design_types import AbstractDesign, ComponentType, DesignComponent
from .base_graph import BaseGraph


class ComponentGraph(BaseGraph[DesignComponent], AbstractDesign):
    @override
    def component(
        self,
        *,
        component_type: Optional[ComponentType] = None,
        subtype: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> DesignComponent:
        return super().component(
            component_type=component_type,
            subtype=subtype,
            name=name,
            **kwargs,
        )

    @override
    def find_components(
        self,
        *,
        component_type: Optional[ComponentType] = None,
        subtype: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list[DesignComponent]:
        candidates: list[DesignComponent] = []
        for component in self.nodes:
            if component_type is not None and component.component_type != component_type:
                continue
            if name is not None and component.id != name:
                continue
            if subtype is not None and component.subtype != subtype:
                continue
            candidates.append(component)
        return candidates
