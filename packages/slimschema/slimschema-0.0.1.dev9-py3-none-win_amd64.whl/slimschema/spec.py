"""@spec decorator for creating validated dataclasses.

The @spec decorator adds json-style methods that mirror stdlib json:
  - loads(json_str) -> instance: Parse JSON string
  - load(dict) -> instance: Load from dict
  - dumps(instance) -> str: Serialize to JSON string
  - dump(instance) -> dict: Serialize to dict
  - json_schema() -> dict: Get JSON Schema
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import MISSING, asdict, dataclass, fields
from datetime import date, datetime
from typing import (
    Annotated,
    Any,
    Literal,
    Union,
    dataclass_transform,
    get_args,
    get_origin,
    get_type_hints,
)
from uuid import UUID

from .backend import validate_json
from .constraints import Alias, Len, Pattern, Range
from .errors import ValidationError
from .formats import Date, DateTime, Email, Url, Uuid

# Type alias for validator functions
ValidatorFunc = Callable[[Any], Any]


class Check:
    """Inline validator constraint.

    Use with Annotated to add custom validation logic.

    Examples:
        def no_admin(v: str) -> str:
            if "admin" in v.lower():
                raise ValueError("cannot contain 'admin'")
            return v

        name: Annotated[str, Len(1, 50), Check(no_admin)]
    """

    __slots__ = ("func",)

    def __init__(self, func: ValidatorFunc) -> None:
        self.func = func

    def __repr__(self) -> str:
        return f"Check({self.func.__name__})"


def _extract_schema(cls: type, hints: dict[str, Any] | None = None) -> dict[str, Any]:
    """Extract JSON Schema from dataclass type hints."""
    if hints is None:
        hints = get_type_hints(cls, include_extras=True)
    properties: dict[str, Any] = {}
    required: list[str] = []

    for f in fields(cls):
        hint = hints[f.name]
        prop, json_name = _type_to_schema(hint, f.name)
        properties[json_name] = prop

        # Required if no default value and no default factory
        if f.default is MISSING and f.default_factory is MISSING:
            required.append(json_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def _type_to_schema(hint: Any, field_name: str = "") -> tuple[dict[str, Any], str]:
    """Convert Python type hint to JSON Schema.

    Returns:
        Tuple of (schema_dict, json_field_name)
    """
    origin = get_origin(hint)
    args = get_args(hint)
    json_name = field_name

    # Annotated[base, constraint, ...]
    if origin is Annotated:
        base_type = args[0]
        constraints = args[1:]
        schema, _ = _type_to_schema(base_type)
        for c in constraints:
            result = _apply_constraint(schema, c)
            if result is not None:
                json_name = result
        return schema, json_name

    # Union (X | Y | None)
    import types

    if origin is Union or origin is types.UnionType:
        non_none = [a for a in args if a is not type(None)]
        has_none = type(None) in args
        if has_none and len(non_none) == 1:
            # Optional - allow null without mutating the base schema.
            schema, _ = _type_to_schema(non_none[0])
            return {"anyOf": [schema, {"type": "null"}]}, json_name

        def _union_schema(member: Any) -> dict[str, Any]:
            if member is type(None):
                return {"type": "null"}
            return _type_to_schema(member)[0]

        return {"anyOf": [_union_schema(a) for a in args]}, json_name

    # Literal["a", "b"]
    if origin is Literal:
        return {"type": "string", "enum": list(args)}, json_name

    # list[T]
    if origin is list:
        items_schema = _type_to_schema(args[0])[0] if args else {}
        return {"type": "array", "items": items_schema}, json_name

    # dict[K, V]
    if origin is dict:
        schema = {"type": "object"}
        if len(args) >= 2:
            # Add value type constraint via additionalProperties
            value_schema = _type_to_schema(args[1])[0]
            if value_schema:
                schema["additionalProperties"] = value_schema
        return schema, json_name

    # Primitives
    if hint is str:
        return {"type": "string"}, json_name
    if hint is int:
        return {"type": "integer"}, json_name
    if hint is float:
        return {"type": "number"}, json_name
    if hint is bool:
        return {"type": "boolean"}, json_name

    # Native Python types with format
    if hint is UUID:
        return {"type": "string", "format": "uuid"}, json_name
    if hint is datetime:
        return {"type": "string", "format": "date-time"}, json_name
    if hint is date:
        return {"type": "string", "format": "date"}, json_name

    # Nested spec
    if hasattr(hint, "_slimschema"):
        return hint._slimschema["schema"], json_name

    return {}, json_name


def _apply_constraint(schema: dict[str, Any], constraint: Any) -> str | None:
    """Apply constraint to schema. Returns alias name if Alias constraint."""
    if isinstance(constraint, Len):
        if schema.get("type") == "string":
            schema["minLength"] = constraint.min
            if constraint.max is not None:
                schema["maxLength"] = constraint.max
        elif schema.get("type") == "array":
            schema["minItems"] = constraint.min
            if constraint.max is not None:
                schema["maxItems"] = constraint.max

    elif isinstance(constraint, Range):
        if constraint.min is not None:
            schema["minimum"] = constraint.min
        if constraint.max is not None:
            schema["maximum"] = constraint.max

    elif isinstance(constraint, Pattern):
        schema["pattern"] = constraint.pattern

    elif isinstance(constraint, Alias):
        return constraint.name

    elif isinstance(constraint, type):
        if constraint is Email:
            schema["format"] = "email"
        elif constraint is Url:
            schema["format"] = "uri"
        elif constraint is Uuid:
            schema["format"] = "uuid"
        elif constraint is Date:
            schema["format"] = "date"
        elif constraint is DateTime:
            schema["format"] = "date-time"

    return None


def _get_alias_map(
    cls: type, hints: dict[str, Any] | None = None
) -> tuple[dict[str, str], dict[str, str]]:
    """Extract alias mappings for load and dump.

    Returns:
        Tuple of (json_name → field_name, field_name → json_name)
    """
    json_to_field: dict[str, str] = {}
    field_to_json: dict[str, str] = {}
    if hints is None:
        hints = get_type_hints(cls, include_extras=True)

    for f in fields(cls):
        hint = hints[f.name]
        origin = get_origin(hint)
        if origin is Annotated:
            for arg in get_args(hint)[1:]:
                if isinstance(arg, Alias):
                    json_to_field[arg.name] = f.name
                    field_to_json[f.name] = arg.name
                    break

    return json_to_field, field_to_json


def _apply_aliases(data: dict[str, Any], alias_map: dict[str, str]) -> dict[str, Any]:
    """Transform aliased keys to field names."""
    result: dict[str, Any] = {}
    for key, value in data.items():
        field_name = alias_map.get(key, key)
        result[field_name] = value
    return result


def _get_validators(
    cls: type, hints: dict[str, Any] | None = None
) -> tuple[dict[str, list[Check]], list[Any], list[Any]]:
    """Extract Check constraints and method validators.

    Returns:
        Tuple of (field_checks, field_validators, model_validators)
    """
    field_checks: dict[str, list[Check]] = {}
    field_validators: list[Any] = []
    model_validators: list[Any] = []

    # Check constraints from type hints
    if hints is None:
        hints = get_type_hints(cls, include_extras=True)
    for f in fields(cls):
        hint = hints[f.name]
        origin = get_origin(hint)
        if origin is Annotated:
            checks = [c for c in get_args(hint)[1:] if isinstance(c, Check)]
            if checks:
                field_checks[f.name] = checks

    # Method validators - check class __dict__ directly for classmethods
    for attr_name, attr_value in vars(cls).items():
        if attr_name.startswith("_"):
            continue
        # Check for classmethod/staticmethod descriptors with validator attributes
        if isinstance(attr_value, classmethod):
            # Access the underlying function via __func__
            if hasattr(attr_value, "_validate_fields"):
                # Store tuple of (bound method, field names)
                method = getattr(cls, attr_name)
                field_validators.append((method, attr_value._validate_fields))
            if hasattr(attr_value, "_validate_model"):
                model_validators.append(getattr(cls, attr_name))
        elif callable(attr_value):
            if hasattr(attr_value, "_validate_fields"):
                field_validators.append((attr_value, attr_value._validate_fields))
            if hasattr(attr_value, "_validate_model"):
                model_validators.append(attr_value)

    return field_checks, field_validators, model_validators


def _instantiate_nested(cls: type, data: dict[str, Any]) -> dict[str, Any]:
    """Recursively instantiate nested @spec classes."""
    hints: dict[str, Any] | None = None
    meta = getattr(cls, "_slimschema", None)
    if isinstance(meta, dict):
        hints = meta.get("hints")
    if hints is None:
        hints = get_type_hints(cls, include_extras=True)
    result: dict[str, Any] = {}

    for key, value in data.items():
        if key not in hints:
            result[key] = value
            continue

        hint = hints[key]
        result[key] = _convert_nested_value(hint, value)

    return result


def _convert_nested_value(hint: Any, value: Any) -> Any:
    """Convert a value to its appropriate nested type."""
    import types

    if value is None:
        return None

    origin = get_origin(hint)
    args = get_args(hint)

    # Handle Annotated
    if origin is Annotated:
        return _convert_nested_value(args[0], value)

    # Handle Union (Optional) - both typing.Union and types.UnionType (X | Y)
    if origin is Union or isinstance(hint, types.UnionType):
        if not args:
            args = get_args(hint)
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return _convert_nested_value(non_none[0], value)

    # Handle list[NestedSpec]
    if origin is list and args:
        item_type = args[0]
        # Check if item type is a @spec class
        if hasattr(item_type, "_slimschema") and isinstance(value, list):
            return [
                item_type.load(item) if isinstance(item, dict) else item
                for item in value
            ]

    # Handle nested @spec class
    if hasattr(hint, "_slimschema") and isinstance(value, dict):
        return hint.load(value)

    # Handle native Python types (convert JSON strings to native objects)
    if hint is UUID and isinstance(value, str):
        return UUID(value)
    if hint is datetime and isinstance(value, str):
        return datetime.fromisoformat(value)
    if hint is date and isinstance(value, str):
        return date.fromisoformat(value)

    return value


def _run_validators(
    cls: type,
    data: dict[str, Any],
    field_checks: dict[str, list[Check]],
    field_validators: list[Any],
    model_validators: list[Any],
) -> dict[str, Any]:
    """Run Python validators after Zig validation."""
    errors: list[dict[str, str]] = []

    # Inline Check constraints
    for name, checks in field_checks.items():
        if name in data:
            for check in checks:
                try:
                    data[name] = check.func(data[name])
                except (ValueError, TypeError) as e:
                    errors.append({"path": f"$.{name}", "message": str(e)})

    # Field validators (methods with @field_validator)
    for method, validate_fields in field_validators:
        for field_name in validate_fields:
            if field_name in data:
                try:
                    data[field_name] = method(data[field_name])
                except (ValueError, TypeError) as e:
                    errors.append({"path": f"$.{field_name}", "message": str(e)})

    # Model validators (methods with @model_validator)
    for method in model_validators:
        try:
            data = method(data)
        except (ValueError, TypeError) as e:
            errors.append({"path": "$", "message": str(e)})

    if errors:
        raise ValidationError(errors)

    return data


@dataclass_transform()
def spec(
    cls: type | None = None,
    *,
    coerce: bool = False,
    frozen: bool = False,
    slots: bool = True,
) -> Any:
    """Decorator that creates a validated dataclass.

    Adds json-style methods (mirrors stdlib json):
      - .loads(json_str) -> instance: Parse JSON string
      - .load(dict) -> instance: Load from dict
      - .dumps(instance) -> str: Serialize to JSON string
      - .dump(instance) -> dict: Serialize to dict
      - .json_schema() -> dict: Get JSON Schema

    Args:
        coerce: Enable type coercion (e.g., "30" -> 30 for int)
        frozen: Make instances immutable
        slots: Use __slots__ for memory efficiency (default True)

    Examples:
        @spec
        class User:
            name: Annotated[str, Len(1, 50)]
            age: Annotated[int, Range(0, 120)]

        user = User.loads('{"name": "Alice", "age": 30}')
        json_str = user.dumps()
    """

    def decorator(cls: type) -> type:
        # Apply dataclass
        dc_cls: type = dataclass(cls, frozen=frozen, slots=slots)

        # Extract schema and validators
        hints = get_type_hints(dc_cls, include_extras=True)
        schema = _extract_schema(dc_cls, hints)
        json_to_field, field_to_json = _get_alias_map(dc_cls, hints)
        field_checks, field_validators, model_validators = _get_validators(dc_cls, hints)

        # Store metadata
        dc_cls._slimschema = {
            "schema": schema,
            "json_to_field": json_to_field,
            "field_to_json": field_to_json,
            "coerce": coerce,
            "hints": hints,
            "field_checks": field_checks,
            "field_validators": field_validators,
            "model_validators": model_validators,
        }

        def loads(cls: type, json_str: str) -> Any:
            """Load instance from JSON string."""
            data = json.loads(json_str)
            return cls.load(data)  # type: ignore[attr-defined]

        def load(cls: type, obj: dict[str, Any]) -> Any:
            """Load instance from dict."""
            meta = cls._slimschema  # type: ignore[attr-defined]

            # Coerce if enabled
            if meta["coerce"]:
                from .coerce import coerce_data

                obj = coerce_data(obj, cls, meta["json_to_field"])

            # Validate with Zig backend
            result = validate_json(meta["schema"], obj)
            if not result.get("valid", False):
                raise ValidationError(result.get("errors", []))

            # Apply aliases to map JSON keys to field names
            if meta["json_to_field"]:
                obj = _apply_aliases(obj, meta["json_to_field"])

            # Run Python validators
            obj = _run_validators(
                cls,
                obj,
                meta["field_checks"],
                meta["field_validators"],
                meta["model_validators"],
            )

            # Instantiate nested @spec classes
            obj = _instantiate_nested(cls, obj)

            return cls(**obj)

        def dump(self: Any) -> dict[str, Any]:
            """Serialize instance to dict."""
            meta = self.__class__._slimschema
            data = asdict(self)

            # Apply reverse aliases (field_name → json_name)
            if meta["field_to_json"]:
                result: dict[str, Any] = {}
                for key, value in data.items():
                    json_key = meta["field_to_json"].get(key, key)
                    result[json_key] = value
                return result

            return data

        def dumps(self: Any) -> str:
            """Serialize instance to JSON string."""
            return json.dumps(self.dump())

        def json_schema(cls: type) -> dict[str, Any]:
            """Get JSON Schema for this class."""
            return cls._slimschema["schema"]  # type: ignore[attr-defined, no-any-return]

        # Class methods for loading
        dc_cls.loads = classmethod(loads)
        dc_cls.load = classmethod(load)

        # Instance methods for dumping
        dc_cls.dump = dump
        dc_cls.dumps = dumps

        dc_cls.json_schema = classmethod(json_schema)

        return dc_cls

    if cls is None:
        return decorator
    return decorator(cls)
