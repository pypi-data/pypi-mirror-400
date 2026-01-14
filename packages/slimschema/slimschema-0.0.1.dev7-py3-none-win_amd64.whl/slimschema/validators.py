"""Validator decorators for custom validation logic."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def field_validator(
    *field_names: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for field validators.

    Use with @classmethod to validate specific fields after Zig validation.

    Examples:
        @spec
        class User:
            name: Annotated[str, Len(1, 50)]

            @field_validator("name")
            @classmethod
            def check_name(cls, v: str) -> str:
                if v.lower() == "admin":
                    raise ValueError("name cannot be 'admin'")
                return v
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._validate_fields = field_names  # type: ignore[attr-defined]
        return func

    return decorator


def model_validator(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for model validators.

    Use with @classmethod to validate the entire model after all fields.

    Examples:
        @spec
        class User:
            name: str
            age: int

            @model_validator
            @classmethod
            def check_model(cls, values: dict) -> dict:
                if values.get("name") == "root" and values.get("age", 0) < 18:
                    raise ValueError("root must be 18+")
                return values
    """
    func._validate_model = True  # type: ignore[attr-defined]
    return func
