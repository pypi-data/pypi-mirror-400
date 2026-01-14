"""Optional Pydantic integration for SlimSchema.

This adapter provides bidirectional conversion between @spec classes and Pydantic models:
- to_pydantic(spec_cls): Convert @spec class → Pydantic BaseModel class
- from_pydantic(model_cls): Convert Pydantic BaseModel class → Schema object

Requires: pip install slimschema[pydantic]
"""

from __future__ import annotations

from dataclasses import MISSING, fields
from typing import TYPE_CHECKING, Annotated, Any, get_args, get_origin, get_type_hints

from ..constraints import Alias, Len, Pattern, Range

if TYPE_CHECKING:
    from ..schema import Schema


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
            _apply_pydantic_constraint(field_kwargs, c)

        return pydantic_type, field_kwargs

    return hint, field_kwargs


def _apply_pydantic_constraint(field_kwargs: dict[str, Any], constraint: Any) -> None:
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


def from_pydantic(model_cls: type) -> Schema:
    """Convert a Pydantic model to a SlimSchema Schema object.

    Extracts the JSON Schema from a Pydantic model and wraps it in a
    SlimSchema Schema object for validation using the Zig backend.

    Args:
        model_cls: A Pydantic BaseModel class

    Returns:
        A Schema object that can be used for validation:
        - schema.validate(data) → ValidationResult
        - schema.validate_json(json_str) → ValidationResult
        - schema.to_json_schema() → dict

    Raises:
        ImportError: If pydantic is not installed
        ValueError: If class is not a Pydantic BaseModel

    Examples:
        from pydantic import BaseModel, Field
        from slimschema import from_pydantic

        class User(BaseModel):
            name: str = Field(min_length=1, max_length=50)
            age: int = Field(ge=0, le=120)

        schema = from_pydantic(User)
        result = schema.validate({"name": "Alice", "age": 30})
        assert result.valid
    """
    try:
        from pydantic import BaseModel
    except ImportError as e:
        raise ImportError(
            "pydantic is required for this adapter. "
            "Install with: pip install slimschema[pydantic]"
        ) from e

    if not (isinstance(model_cls, type) and issubclass(model_cls, BaseModel)):
        raise ValueError(f"{model_cls.__name__} is not a Pydantic BaseModel")

    # Import Schema here to avoid circular imports
    from ..schema import Schema

    # Extract JSON Schema from Pydantic model
    json_schema = model_cls.model_json_schema()

    # Resolve $defs references for nested models (inline them for Zig validation)
    json_schema = _resolve_refs(json_schema)

    return Schema.from_json_schema(json_schema)


def _resolve_refs(schema: dict[str, Any]) -> dict[str, Any]:
    """Resolve $ref references by inlining definitions.

    Pydantic generates JSON Schema with $defs for nested models.
    This function inlines those references for Zig validation.

    Handles recursive models by detecting cycles and leaving recursive
    $ref references intact (along with their $defs) rather than
    inlining them infinitely.
    """
    if "$defs" not in schema and "definitions" not in schema:
        return schema

    defs_key = "$defs" if "$defs" in schema else "definitions"
    defs = schema.get(defs_key, {})
    kept_refs: set[str] = set()  # Track refs that couldn't be inlined (recursive)

    def resolve(obj: Any, resolving: frozenset[str] | None = None) -> Any:
        if resolving is None:
            resolving = frozenset()

        if isinstance(obj, dict):
            if "$ref" in obj:
                ref_path = obj["$ref"]
                def_name = None

                # Handle #/$defs/ModelName or #/definitions/ModelName
                if ref_path.startswith("#/$defs/"):
                    def_name = ref_path[8:]
                elif ref_path.startswith("#/definitions/"):
                    def_name = ref_path[14:]

                if def_name and def_name in defs:
                    # Cycle detection: if we're already resolving this ref, leave it intact
                    if def_name in resolving:
                        kept_refs.add(def_name)
                        return obj
                    # Resolve the reference with updated seen set
                    return resolve(defs[def_name], resolving | {def_name})
                return obj
            return {k: resolve(v, resolving) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve(item, resolving) for item in obj]
        return obj

    resolved = resolve(schema)

    # Only remove $defs if no refs were kept; otherwise keep needed definitions
    if kept_refs:
        # Keep only the definitions that are still referenced
        kept_defs = {name: resolve(defs[name], frozenset({name})) for name in kept_refs}
        resolved[defs_key] = kept_defs
    else:
        # Remove $defs/definitions from the resolved schema
        resolved.pop("$defs", None)
        resolved.pop("definitions", None)

    return resolved
