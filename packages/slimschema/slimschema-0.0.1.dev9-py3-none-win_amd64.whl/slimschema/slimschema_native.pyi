"""Type stubs for slimschema_native extension module.

This module provides native JSON Schema validation using a Zig backend.
Follows the Native CPython Extension Standard with heap types and buffer protocol.
"""

from typing import Any

class ValidationError:
    """A validation error with path and message.

    Attributes:
        path: JSON path to the error location (e.g., "$.items[0].name")
        message: Human-readable error message
    """

    path: str
    message: str

    def __repr__(self) -> str: ...

class ValidationResult:
    """Validation result with valid flag and errors list.

    Can be used as a boolean (True if validation passed).

    Attributes:
        valid: True if validation passed, False otherwise
        errors: List of ValidationError objects (empty if valid)
    """

    valid: bool
    errors: list[ValidationError]

    def __repr__(self) -> str: ...
    def __bool__(self) -> bool: ...

def validate_json(schema: dict[str, Any], data: Any) -> ValidationResult:
    """Validate data against JSON Schema.

    Args:
        schema: JSON Schema dictionary
        data: Data to validate (any JSON-serializable Python object)

    Returns:
        ValidationResult with valid flag and errors list

    Raises:
        TypeError: If schema is not a dict
        ValueError: If schema or data cannot be serialized to JSON
    """
    ...

def validate_json_bytes(
    schema: dict[str, Any], data: bytes | bytearray | memoryview | str
) -> ValidationResult:
    """Validate JSON bytes against schema (fast path).

    Uses buffer protocol to pass bytes directly to the native extension
    without Python-side parsing. This is the fastest validation path.

    Args:
        schema: JSON Schema dictionary
        data: JSON data as bytes, bytearray, memoryview, or str

    Returns:
        ValidationResult with valid flag and errors list

    Raises:
        TypeError: If schema is not a dict or data is not a valid buffer
        ValueError: If schema cannot be serialized or data is not valid JSON
    """
    ...

def get_version() -> str:
    """Get native module version.

    Returns:
        Version string (e.g., "0.3.0")
    """
    ...
