"""Type coercion for flexible input parsing."""

from __future__ import annotations

from dataclasses import fields
from typing import Annotated, Any, Union, get_args, get_origin, get_type_hints


def coerce_value(value: Any, target_type: type) -> Any:
    """Coerce value to target type.

    Args:
        value: Value to coerce
        target_type: Target type to coerce to

    Returns:
        Coerced value

    Raises:
        TypeError: If coercion is not possible
    """
    if isinstance(value, target_type):
        return value

    try:
        if target_type is int:
            if isinstance(value, str):
                return int(value)
            if isinstance(value, float):
                return int(value)

        if target_type is float:
            if isinstance(value, (str, int)):
                return float(value)

        if target_type is bool:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)

        if target_type is str:
            return str(value)
    except ValueError as e:
        msg = f"Cannot coerce {type(value).__name__} to {target_type.__name__}"
        raise TypeError(msg) from e

    raise TypeError(f"Cannot coerce {type(value).__name__} to {target_type.__name__}")


def _get_base_type(hint: Any) -> type | None:
    """Extract base type from type hint."""
    import types

    origin = get_origin(hint)
    args = get_args(hint)

    # Annotated[base, ...]
    if origin is Annotated:
        return _get_base_type(args[0])

    # Union/Optional - handle both typing.Union and types.UnionType (X | Y)
    if origin is Union or isinstance(hint, types.UnionType):
        if not args:
            args = get_args(hint)
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            return _get_base_type(non_none[0])
        return None

    # list[T] - coerce items
    if origin is list:
        return list

    # Primitives
    if hint in (str, int, float, bool):
        return hint  # type: ignore[no-any-return]

    return None


def coerce_data(
    data: dict[str, Any], cls: type, alias_map: dict[str, str] | None = None
) -> dict[str, Any]:
    """Coerce data dict values to match class field types.

    Args:
        data: Input data dict
        cls: Target dataclass type
        alias_map: Optional mapping from alias -> field_name

    Returns:
        Coerced data dict
    """
    hints: dict[str, Any] | None = None
    meta = getattr(cls, "_slimschema", None)
    if isinstance(meta, dict):
        hints = meta.get("hints")
    if hints is None:
        hints = get_type_hints(cls, include_extras=True)
    result = dict(data)

    # Build reverse alias map (field_name -> alias)
    field_to_alias: dict[str, str] = {}
    if alias_map:
        field_to_alias = {v: k for k, v in alias_map.items()}

    for f in fields(cls):
        # Check for field by name or alias
        key = f.name
        if f.name not in result and f.name in field_to_alias:
            key = field_to_alias[f.name]
        if key not in result:
            continue

        hint = hints[f.name]
        target_type = _get_base_type(hint)

        if target_type is None:
            continue

        value = result[key]

        # Handle list coercion
        if target_type is list:
            origin = get_origin(hint)
            if origin is Annotated:
                hint = get_args(hint)[0]
                origin = get_origin(hint)

            if origin is list:
                item_args = get_args(hint)
                if item_args:
                    item_type = _get_base_type(item_args[0])
                    if item_type and isinstance(value, list):
                        result[key] = [
                            (
                                coerce_value(v, item_type)
                                if not isinstance(v, item_type)
                                else v
                            )
                            for v in value
                        ]
            continue

        # Coerce primitive
        if not isinstance(value, target_type):
            try:
                result[key] = coerce_value(value, target_type)
            except (TypeError, ValueError):
                pass  # Let validation handle the error

    return result
