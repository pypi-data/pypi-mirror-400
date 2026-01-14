from contextlib import ExitStack
from typing import Any, Literal, Optional, cast, override

import pandas as pd

from .step_table_types import AbstractStepTable, StepRecipe, StepTableRequest, StepTablePlan
from ...modeling.base_model_context import BaseModelContext
from ...modeling.hooks import SerializedHook, deserialize_hook, Hook
from ...modeling.resource_type_helpers import ResourceTypeDescriptor, ResourceTypeClass
from ...modeling.basics import ResourceTypeExtended
from ...modeling.utils import aggregate_series
from ...display.waterfall import display_waterfall
from ...common.common_utils import pick_dict_keys


# When creating step tables and waterfalls, the derived step-series should not inherit all attrs
# This avoids unintended inheritance and given that hooks are accumulated the final attrs become ambiguous
_white_list_attrs = [
    'unit',
    'agg',
    'resource_type',
    'freq',
    'label',
    'origin',
]


class StepTable(AbstractStepTable):
    @property
    def _constructor(self):
        return StepTable

    @override
    def to_step_dict(self) -> dict[str, Any]:
        result = {}
        for col in self.columns:
            result[col] = aggregate_series(self[col])
        return result

    @override
    def make_waterfall_table(
        self,
        resource_type: Optional[ResourceTypeExtended | list[ResourceTypeExtended]] = None,
        final_step_name: str = '',  # additional column only created if name is provided
    ) -> 'StepTable':
        return make_waterfall_table(self, resource_type=resource_type, final_step_name=final_step_name)

    @override
    def display_waterfall(
        self,
        figsize: Optional[tuple[float | None, float | None]] = None,
        title: str = '',
        add_percentages: bool = True,
        renderer: Optional[Literal['plotly', 'kaleido']] = None,
    ):
        return display_waterfall(
            self,
            figsize=figsize,
            title=title,
            add_percentages=add_percentages,
            renderer=renderer,
        )


def make_waterfall_table(
    table: pd.DataFrame,
    *,
    resource_type: Optional[ResourceTypeExtended | list[ResourceTypeExtended]] = None,
    final_step_name: str = '',  # additional column only created if name is provided
) -> StepTable:
    diff_data = {}
    previous_series = None
    current_series = None

    if resource_type is not None:
        if not isinstance(resource_type, list):
            resource_type = [resource_type]
        resource_type_strs = [str(rt) for rt in resource_type]
        filtered_columns = []
        for col in table.columns:
            col_resource_type = table[col].attrs.get('resource_type')
            if col_resource_type in resource_type_strs:
                filtered_columns.append(col)
        table = table[filtered_columns]

    for col in table.columns:
        current_series = table[col]
        if previous_series is None:
            diff_data[col] = current_series
            new_attrs = pick_dict_keys(diff_data[col].attrs, _white_list_attrs)
            new_attrs['waterfall_measure'] = 'absolute'
            diff_data[col].attrs = new_attrs
        else:
            diff_data[col] = current_series - previous_series
            new_attrs = pick_dict_keys(diff_data[col].attrs, _white_list_attrs)
            new_attrs['waterfall_measure'] = 'relative'
            diff_data[col].attrs = new_attrs
        previous_series = current_series

    result = StepTable(diff_data, index=table.index)
    if final_step_name and current_series is not None:
        result[final_step_name] = current_series

        result[final_step_name].attrs = current_series.attrs.copy()
        result[final_step_name].attrs['waterfall_measure'] = 'absolute'
        if result[final_step_name].attrs.get('label'):  # explicitly disallow same label as original series
            result[final_step_name].attrs['label'] = final_step_name

    for col in diff_data.keys():
        result[col].attrs = diff_data[col].attrs.copy()
    return result


def _ensure_step_table_request(steps: StepTableRequest | StepTablePlan, target: Any = None) -> StepTableRequest:
    if isinstance(steps, dict):
        if 'steps' not in steps:
            raise ValueError('StepTableRequest must contain "steps" key')
        return steps
    else:
        request_steps: list[StepRecipe] = []
        for name, raw_hooks in steps:
            effective_hooks = raw_hooks
            if effective_hooks is None:
                effective_hooks = []
            if not isinstance(effective_hooks, list):
                effective_hooks = [effective_hooks]
            request_steps.append(
                {
                    'name': name,
                    'hooks': effective_hooks,
                }
            )

        return {
            'steps': request_steps,
            'target': target,
        }


def make_step_table(
    context: BaseModelContext,
    steps: StepTableRequest | StepTablePlan,
    *,
    target: Any = None,
) -> StepTable:
    step_table_request = _ensure_step_table_request(steps, target=target)
    index_len = None
    result_map = {}
    last_result = None
    with ExitStack() as stack:
        for step_index, step in enumerate(step_table_request['steps']):
            ################ Prepare hooks

            raw_hooks = step['hooks'] if step is not None else []
            hooks = []
            for hook_index, raw_hook in enumerate(raw_hooks):
                hook = None
                if isinstance(raw_hook, dict):
                    raw_hook = cast(SerializedHook, raw_hook)
                    hook = deserialize_hook(raw_hook)
                    assert hook is not None, f'Hook deserialization failed. Step {step_index}, hook {hook_index}'
                elif isinstance(raw_hook, Hook):
                    hook = raw_hook
                else:
                    raise NotImplementedError(f'Unsupported hook in step {step_index}, hook {hook_index}: {type(raw_hook)}')
                hooks.append(hook)
            stack.enter_context(context.hooks(*hooks))

            ################ Execute target

            result = None
            raw_target = step['target'] if step is not None and 'target' in step else step_table_request.get('target')
            if isinstance(raw_target, (str)):
                result = context.resource({'resource_type': raw_target})
            elif isinstance(raw_target, (dict, ResourceTypeClass, ResourceTypeDescriptor)):
                result = context.resource(raw_target)
            elif callable(raw_target):
                result = raw_target(context=context, step_recipe=step, previous_result=last_result)
            else:
                raise NotImplementedError(f'Unsupported target in step {step_index}: {type(raw_target)}')

            last_result = result

            ################ Turn result into one or more pd.Series

            series_list = []
            if isinstance(result, (int, float)):
                series_list.append(pd.Series([result]))
            elif isinstance(result, pd.DataFrame):
                for col in result.columns:
                    series_list.append(result[col])
            elif isinstance(result, pd.Series):
                series_list.append(result)
            elif isinstance(result, (list, tuple)):
                for item in result:  # pyright: ignore[reportGeneralTypeIssues]
                    assert isinstance(item, pd.Series), (
                        f'Step result list items must be pd.Series, got {type(item)} in step {step_index}'
                    )
                    series_list.append(item)
            else:
                raise NotImplementedError(f'Unsupported step result type in step {step_index}: {type(result)}')

            ################ Generate names for the new series

            names = []
            name = step['name'] if step is not None else f'step_{step_index}'

            if len(series_list) == 1:
                names.append(name)
            elif len(series_list) > 1:
                for series_index, one_series in enumerate(series_list):
                    series_label = one_series.name
                    if series_label is None:
                        series_label = one_series.attrs.get('label')
                    if series_label is None:
                        series_label = f'{series_index}'
                    names.append(f'{name}_{series_label}')

            ################ Insert series into result map, checking index lengths

            for series_index, one_series in enumerate(series_list):
                if index_len is None:
                    index_len = len(one_series.index)
                else:
                    if len(one_series.index) != index_len:
                        raise ValueError(
                            f'Step result series length mismatch in step {step_index}: '
                            f'expected {index_len}, got {len(one_series.index)}'
                        )
                one_series.attrs['step_index'] = step_index
                one_series.attrs['label'] = names[series_index]
                result_map[names[series_index]] = one_series

    if len(result_map) == 0:
        raise ValueError('No results generated in step table')

    result = StepTable(result_map, index=result_map[next(iter(result_map))].index)
    for index, (key, series) in enumerate(result_map.items()):
        if index == 0:
            result[key].attrs = series.attrs
        else:
            result[key].attrs = pick_dict_keys(series.attrs, [*_white_list_attrs, 'step_index'])
    return result
