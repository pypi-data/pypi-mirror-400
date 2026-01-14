from abc import abstractmethod
from typing import Any, Literal, NotRequired, Optional, Sequence, TypedDict
import pandas as pd

from ...modeling.basics import ResourceTypeExtended
from ...modeling.utils import aggregate_table

"""Compact way to define StepTableRequest:
[('original', None), ('with_soiling', for_resource('soiling_loss').use(my_model))]
"""
type StepTablePlan = Sequence[tuple[str, Any]]

WaterfallMeasure = Literal['initial', 'absolute', 'relative', 'total']


class WaterfallItem(TypedDict):
    key: str
    value: float | int
    measure: WaterfallMeasure
    unit: NotRequired[str]


class StepRecipe(TypedDict):
    """Describes one transformation step.

    Attributes:
        name: Internal step name.
        label: Optional human-readable label.
        hooks: List of hook callables applied to the model inputs.
        target: what the step produces. This overrides the target of StepTableRequest:
            - resource_type (str or class)
            - list of resource_type-s
            - a callable (*, context, step_recipe, previous_result) -> pd.DataFrame | pd.Series
    """

    name: str
    label: NotRequired[str]
    hooks: list[Any]
    target: NotRequired[Any]


class StepTableRequest(TypedDict):
    """Describes a request to generate a step table.

    Attributes:
        steps: List of step recipes or None (to copy previous step).
        target: what the overall step table produces:
            - resource_type (str or class)
            - list of resource_type-s
            - a callable (context,step_table_request) -> pd.DataFrame
    """

    steps: list[StepRecipe]
    target: NotRequired[Any]


class AbstractStepTable(pd.DataFrame):
    def to_step_dict(self) -> dict[str, Any]:
        collapsed = aggregate_table(self)
        result = {}
        for col in self.columns:
            result[col] = collapsed[col].iloc[0]
        return result

    @abstractmethod
    def make_waterfall_table(
        self,
        resource_type: Optional[ResourceTypeExtended | list[ResourceTypeExtended]] = None,
        final_step_name: str = '',  # additional column only created if name is provided
    ) -> 'AbstractStepTable': ...

    def to_waterfall_items(self) -> list[WaterfallItem]:
        collapsed = aggregate_table(self)
        result: list[WaterfallItem] = []
        for col_index, col in enumerate(self.columns):
            value = collapsed[col].iloc[0]
            default_measure = 'initial' if col_index == 0 else 'relative'
            measure = collapsed[col].attrs.get('waterfall_measure', default_measure)
            item = WaterfallItem(key=col, value=value, measure=measure)
            if 'unit' in collapsed[col].attrs:
                item['unit'] = collapsed[col].attrs['unit']
            result.append(item)
        return result

    @abstractmethod
    def display_waterfall(
        self,
        figsize: Optional[tuple[float | None, float | None]] = None,
        title: str = '',
        add_percentages: bool = True,
        renderer: Optional[Literal['plotly', 'kaleido']] = None,
    ): ...
