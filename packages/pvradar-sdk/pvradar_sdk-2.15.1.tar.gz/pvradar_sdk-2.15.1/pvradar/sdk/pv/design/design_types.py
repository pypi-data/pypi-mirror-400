from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal, Optional, Any, override


ComponentType = Literal[
    'other',  # a generic component for types that aren't part of SDK yet (use subtype to narrow down)
    'bess',
    'battery',
    'pv',
    'inverter',
    'array',
    'module',
    'structure',
    'transformer',
    'grid',
]

_component_counter = 0


def get_next_component_id() -> str:
    global _component_counter
    _component_counter += 1
    return f'default_{_component_counter}'


@dataclass(kw_only=True)
class DesignComponent(ABC):
    id: str = field(default_factory=get_next_component_id)
    subtype: Optional[str] = None
    specs: dict[str, Any] = field(default_factory=dict)

    @property
    @abstractmethod
    def component_type(self) -> ComponentType: ...


@dataclass(kw_only=True)
class CustomDesignComponent(DesignComponent):
    type: ComponentType

    @property
    @override
    def component_type(self) -> ComponentType:
        return self.type


class AbstractDesign:
    def component(self, *args, **kwargs) -> DesignComponent:
        candidates = self.find_components(*args, **kwargs)
        candidate_len = len(list(candidates))
        if candidate_len > 1:
            raise ValueError(f'Multiple components found matching criteria ({candidate_len} found)')

        if candidate_len == 0:
            raise ValueError(f'No component found for kwargs: {kwargs}')

        result = next(iter(candidates))
        if result is None:
            raise ValueError('Component turned out to be None: {kwargs}')
        return result

    @abstractmethod
    def find_components(self, *args, **kwargs) -> list[DesignComponent]: ...
