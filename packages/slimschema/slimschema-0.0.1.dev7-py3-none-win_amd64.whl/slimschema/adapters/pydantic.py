"""Optional Pydantic integration for SlimSchema.

This adapter converts @spec classes to Pydantic models for interoperability
with Pydantic-based ecosystems.

Requires: pip install slimschema[pydantic]
"""

from __future__ import annotations

from dataclasses import MISSING, fields
from typing import Annotated, Any, get_args, get_origin, get_type_hints

from ..constraints import Alias, Len, Pattern, Range


def to_pydantic(spec_cls: type) -> type:
    """Convert a @spec class to a Pydantic model.

    Args:
        spec_cls: A class decorated with @spec

    Returns:
        A Pydantic BaseModel class with equivalent validation

    Raises:
        ImportError: If pydantic is not installed
        ValueError: If class is not a @spec class

    Examples:
        from slimschema import spec, Len
        from slimschema.adapters.pydantic import to_pydantic
        from typing import Annotated

        @spec
        class User:
            name: Annotated[str, Len(1, 50)]

        UserModel = to_pydantic(User)
        user = UserModel.model_validate_json('{"name": "Alice"}')
    """
    try:
        from pydantic import BaseModel, Field
    except ImportError as e:
        raise ImportError(
            "pydantic is required for this adapter. "
            "Install with: pip install slimschema[pydantic]"
        ) from e

    if not hasattr(spec_cls, "_slimschema"):
        raise ValueError(f"{spec_cls.__name__} is not a @spec class")

    hints = get_type_hints(spec_cls, include_extras=True)
    annotations: dict[str, Any] = {}
    field_defaults: dict[str, Any] = {}

    for f in fields(spec_cls):
        hint = hints[f.name]
        pydantic_type, field_kwargs = _convert_type(hint)

        annotations[f.name] = pydantic_type

        if f.default is not MISSING:
            field_kwargs["default"] = f.default
        elif f.default_factory is not MISSING:
            field_kwargs["default_factory"] = f.default_factory

        if field_kwargs:
            field_defaults[f.name] = Field(**field_kwargs)

    namespace = {"__annotations__": annotations, **field_defaults}
    return type(spec_cls.__name__, (BaseModel,), namespace)


def _convert_type(hint: Any) -> tuple[Any, dict[str, Any]]:
    """Convert SlimSchema type hint to Pydantic type and Field kwargs."""
    origin = get_origin(hint)
    args = get_args(hint)
    field_kwargs: dict[str, Any] = {}

    if origin is Annotated:
        base_type = args[0]
        constraints = args[1:]

        pydantic_type, base_kwargs = _convert_type(base_type)
        field_kwargs.update(base_kwargs)

        for c in constraints:
            _apply_pydantic_constraint(field_kwargs, c, pydantic_type)

        return pydantic_type, field_kwargs

    return hint, field_kwargs


def _apply_pydantic_constraint(
    field_kwargs: dict[str, Any], constraint: Any, hint_type: Any
) -> None:
    """Apply SlimSchema constraint to Pydantic Field kwargs."""
    if isinstance(constraint, Len):
        # min_length works for both strings and lists in Pydantic
        field_kwargs["min_length"] = constraint.min
        if constraint.max is not None:
            field_kwargs["max_length"] = constraint.max

    elif isinstance(constraint, Range):
        if constraint.min is not None:
            field_kwargs["ge"] = constraint.min
        if constraint.max is not None:
            field_kwargs["le"] = constraint.max

    elif isinstance(constraint, Pattern):
        field_kwargs["pattern"] = constraint.pattern

    elif isinstance(constraint, Alias):
        field_kwargs["alias"] = constraint.name
