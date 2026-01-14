"""SlimSchema - Fast schema validation using Zig backend.

Example:
    from slimschema import spec, Len, Range, Email
    from typing import Annotated, Literal

    @spec
    class User:
        name: Annotated[str, Len(1, 50)]
        age: Annotated[int, Range(0, 120)]
        email: Annotated[str, Email]
        status: Literal["active", "pending"]

    user = User.parse('{"name": "Alice", "age": 30, ...}')
"""

from dataclasses import field

from .backend import parse_yaml, to_yaml
from .constraints import Alias, Len, Pattern, Range
from .errors import ValidationError
from .formats import Date, DateTime, Email, Url, Uuid
from .schema import Schema, SchemaError, ValidationResult
from .spec import Check, spec
from .validators import field_validator, model_validator

__version__ = "0.0.1dev0"


def to_pydantic(spec_cls: type) -> type:
    """Convert a @spec class to a Pydantic model.

    Requires: pip install slimschema[pydantic]
    """
    from .adapters.pydantic import to_pydantic as _to_pydantic

    return _to_pydantic(spec_cls)


__all__ = [
    # Decorator
    "spec",
    # Dataclass re-export
    "field",
    # Schema class (YAML-based API)
    "Schema",
    "SchemaError",
    "ValidationResult",
    # Constraints
    "Len",
    "Range",
    "Pattern",
    "Alias",
    # Formats
    "Email",
    "Url",
    "Uuid",
    "Date",
    "DateTime",
    # Validators
    "Check",
    "field_validator",
    "model_validator",
    # Errors
    "ValidationError",
    # Adapters
    "to_pydantic",
    # YAML parsing/generation
    "parse_yaml",
    "to_yaml",
]
