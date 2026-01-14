"""Validation error types."""

from __future__ import annotations


class ValidationError(Exception):
    """Raised when validation fails.

    Attributes:
        errors: List of error details with path and message.
    """

    def __init__(self, errors: list[dict[str, str]]) -> None:
        self.errors = errors
        messages = "; ".join(
            f"{e.get('path', '')}: {e.get('message', e.get('msg', 'unknown'))}"
            for e in errors
        )
        super().__init__(f"Validation failed: {messages}")
