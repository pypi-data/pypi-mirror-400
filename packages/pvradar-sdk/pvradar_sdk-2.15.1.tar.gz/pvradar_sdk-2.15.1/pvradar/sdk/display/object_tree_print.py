from dataclasses import fields, is_dataclass
from typing import override
import inspect


class TreePrintable:
    INDENT = '  '
    NAME_WIDTH = 40

    @override
    def __str__(self) -> str:
        return self._format_root(self)

    @classmethod
    def _format_root(cls, obj) -> str:
        lines = ['└── ' + obj.__class__.__name__]
        items = cls._collect_items(obj)
        prefix = cls.INDENT

        for i, (name, value) in enumerate(items):
            is_last = i == len(items) - 1

            block = cls._format_item(
                name=name,
                value=value,
                prefix=prefix,
                is_last=is_last,
            )
            lines.extend(block)

            # continuation line between root-level items (kept as-is)
            if not is_last:
                cont_prefix = prefix + '│   '
                lines.append(cont_prefix)

        return '\n'.join(lines)

    @classmethod
    def _collect_items(cls, obj):
        items = []

        EXCLUDE_NAMES = {
            'VARS',
            'EQUATIONS',
            '_abc_impl',
            'solved',
            'nodes',
            'edges',
        }

        # --- dataclass fields ---
        dataclass_field_names = {f.name for f in fields(obj)}
        for f in fields(obj):
            if f.name in EXCLUDE_NAMES:
                continue
            value = getattr(obj, f.name)
            if value is None:
                continue
            items.append((f.name, value))

        # --- properties ---
        property_names = {name for name, prop in inspect.getmembers(obj.__class__, lambda x: isinstance(x, property))}
        for name in property_names:
            if name in EXCLUDE_NAMES:
                continue
            if obj.__class__.__name__ == 'RigidDesign' and name == 'array':
                continue
            try:
                value = getattr(obj, name)
            except Exception:
                continue
            if value is None:
                continue
            items.append((name, value))

        # --- class-level constants, but filtered ---
        for name, raw_value in obj.__class__.__dict__.items():
            if (
                name in EXCLUDE_NAMES
                or name in dataclass_field_names
                or name in property_names
                or name.startswith('__')
                or name.endswith('__')
                or callable(raw_value)
            ):
                continue

            try:
                value = getattr(obj, name)
            except Exception:
                continue
            if value is None:
                continue
            items.append((name, value))

        # scalars first, nested after; alphabetical within each group
        def sort_key(item):
            name, value = item
            is_nested = is_dataclass(value) and isinstance(value, TreePrintable)
            return (1 if is_nested else 0, name.lower())

        items.sort(key=sort_key)
        return items

    @classmethod
    def _format_item(cls, *, name: str, value, prefix: str, is_last: bool):
        connector = '└── ' if is_last else '├── '
        line_prefix = prefix + connector

        # 1) Special case: arrays -> header + recurse into FIRST item (inline)
        if name == 'arrays' and isinstance(value, (list, tuple)):
            count = len(value)
            if count > 0 and is_dataclass(value[0]) and isinstance(value[0], TreePrintable):
                first_array = value[0]
                class_name = first_array.__class__.__name__
                plural = 'item' if count == 1 else 'items'

                header = f'{name} [{class_name}] ({count} {plural})'
                lines = [line_prefix + header]

                # prefix used for children of "arrays"
                child_prefix = prefix + ('    ' if is_last else '│   ')
                sub_items = cls._collect_items(first_array)

                printed_any = False
                for i, (sub_name, sub_value) in enumerate(sub_items):
                    sub_last = i == len(sub_items) - 1
                    is_nested_component = is_dataclass(sub_value) and isinstance(sub_value, TreePrintable)

                    # IMPORTANT: add aligned empty connector line BEFORE each nested component
                    # but only if something has already been printed at this level
                    if is_nested_component and printed_any:
                        lines.append(child_prefix + '│')

                    block = cls._format_item(
                        name=sub_name,
                        value=sub_value,
                        prefix=child_prefix,
                        is_last=sub_last,
                    )
                    lines.extend(block)
                    printed_any = True

                return lines

            return [line_prefix + f'{name}: []']

        # 2) Nested design object
        if is_dataclass(value) and isinstance(value, TreePrintable):
            class_name = value.__class__.__name__
            header = f'{name} [{class_name}]'
            lines = [line_prefix + header]

            child_prefix = prefix + ('    ' if is_last else '│   ')
            sub_items = cls._collect_items(value)

            printed_any = False
            for i, (sub_name, sub_value) in enumerate(sub_items):
                sub_last = i == len(sub_items) - 1
                is_nested_component = is_dataclass(sub_value) and isinstance(sub_value, TreePrintable)

                # IMPORTANT: add aligned empty connector line BEFORE each nested component
                # but only if something has already been printed at this level
                if is_nested_component and printed_any:
                    lines.append(child_prefix + '│')

                block = cls._format_item(
                    name=sub_name,
                    value=sub_value,
                    prefix=child_prefix,
                    is_last=sub_last,
                )
                lines.extend(block)
                printed_any = True

            return lines

        # 3) Generic list/tuple (not "arrays")
        if isinstance(value, (list, tuple)):
            lines = [line_prefix + f'{name} (list)']
            child_prefix = prefix + ('    ' if is_last else '│   ')

            for i, item in enumerate(value):
                last_item = i == len(value) - 1
                item_connector = '└── ' if last_item else '├── '
                item_prefix = child_prefix + item_connector

                if is_dataclass(item) and isinstance(item, TreePrintable):
                    class_name = item.__class__.__name__
                    lines.append(item_prefix + class_name)
                else:
                    lines.append(item_prefix + str(item))
            return lines

        # 4) Scalar value
        padded = name.ljust(cls.NAME_WIDTH)
        return [line_prefix + f'{padded}: {value}']
