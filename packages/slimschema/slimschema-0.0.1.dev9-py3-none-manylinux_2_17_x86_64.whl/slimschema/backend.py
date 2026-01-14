"""JSON Schema validation backend.

Uses native Zig validation when available, falling back to jsonschema library.
The native backend is ~10-100x faster than jsonschema for typical schemas.

The native extension follows the Native CPython Extension Standard:
- Heap types (ValidationResult, ValidationError) created in compiled code
- GIL released during validation
- Buffer protocol support for bytes/bytearray/memoryview input
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

# Type for the native validation function - returns ValidationResult heap type
_ValidateFn = Callable[[dict[str, Any], Any], Any]
_ValidateBytesF = Callable[[dict[str, Any], bytes | bytearray | memoryview | str], Any]
_ParseYamlFn = Callable[[str], dict[str, Any]]
_ParseYamlSafeFn = Callable[[str], tuple[dict[str, Any] | None, list[dict[str, Any]]]]
_ToYamlFn = Callable[[str, int], str]


class ValidationErrorLike(Protocol):
    """Protocol for ValidationError objects."""

    path: str
    message: str


class ValidationResultLike(Protocol):
    """Protocol for ValidationResult objects."""

    valid: bool
    errors: list[ValidationErrorLike]


# Try to import native CPython extension (slimschema_native).
#
# We support multiple layouts:
# - top-level `slimschema_native` module (e.g., `zig-out/python` in dev/CI)
# - packaged as `slimschema.slimschema_native` (wheel layout)
# - packaged as `slimschema._native.slimschema_native` (local build output)
_native_available = False
_native_validate: _ValidateFn | None = None
_native_validate_bytes: _ValidateBytesF | None = None
_native_parse_yaml: _ParseYamlFn | None = None
_native_parse_yaml_safe: _ParseYamlSafeFn | None = None
_native_to_yaml: _ToYamlFn | None = None
_native_version: str | None = None
_ValidationResult: type | None = None
_ValidationError: type | None = None

try:
    import slimschema_native as _native_mod
except (ImportError, OSError):
    _native_mod = None  # type: ignore[assignment]

if _native_mod is None:
    try:
        from . import slimschema_native as _native_mod
    except (ImportError, OSError):
        _native_mod = None  # type: ignore[assignment]

if _native_mod is None:
    try:
        from ._native import slimschema_native as _native_mod
    except (ImportError, OSError):
        _native_mod = None  # type: ignore[assignment]

if _native_mod is not None:
    _native_available = True
    _native_validate = _native_mod.validate_json
    _native_validate_bytes = getattr(_native_mod, "validate_json_bytes", None)
    _native_parse_yaml = getattr(_native_mod, "parse_yaml", None)
    _native_parse_yaml_safe = getattr(_native_mod, "parse_yaml_safe", None)
    _native_to_yaml = getattr(_native_mod, "to_yaml", None)
    _ValidationResult = getattr(_native_mod, "ValidationResult", None)
    _ValidationError = getattr(_native_mod, "ValidationError", None)
    try:
        _native_version = _native_mod.get_version()
    except Exception:
        _native_version = None

del _native_mod


def is_native_available() -> bool:
    """Check if native validation backend is available."""
    return _native_available


def _result_to_dict(result: Any) -> dict[str, Any]:
    """Convert ValidationResult heap type to dict for backward compatibility."""
    # If it's already a dict (old-style or jsonschema fallback), return as-is
    if isinstance(result, dict):
        return result

    # Convert ValidationResult heap type to dict
    # This supports both the native heap type and any duck-typed object
    try:
        errors = []
        if hasattr(result, "errors") and result.errors:
            for err in result.errors:
                errors.append({"path": err.path, "message": err.message})

        if result.valid:
            return {"valid": True}
        return {"valid": False, "errors": errors}
    except (AttributeError, TypeError):
        # Fallback if structure is unexpected
        return {"valid": bool(result), "errors": []}


def validate_json(schema: dict[str, Any], data: Any) -> dict[str, Any]:
    """Validate data against schema.

    Uses native Zig validation when available, otherwise falls back to jsonschema.

    Args:
        schema: JSON Schema dictionary
        data: Data to validate (already parsed from JSON)

    Returns:
        Dict with "valid" boolean and optionally "errors" list
    """
    # Try native validation first
    if _native_available and _native_validate is not None:
        result = _native_validate(schema, data)
        return _result_to_dict(result)

    # Fall back to jsonschema
    return _validate_with_jsonschema(schema, data)


def validate_json_bytes(
    schema: dict[str, Any], data: bytes | bytearray | memoryview | str
) -> dict[str, Any]:
    """Validate JSON bytes against schema.

    Fast path for validating raw JSON bytes without Python-side parsing.
    Uses buffer protocol to pass bytes directly to native extension.

    Args:
        schema: JSON Schema dictionary
        data: JSON data as bytes, bytearray, memoryview, or str

    Returns:
        Dict with "valid" boolean and optionally "errors" list
    """
    if _native_available and _native_validate_bytes is not None:
        result = _native_validate_bytes(schema, data)
        return _result_to_dict(result)

    # Fall back to regular validation (parse bytes to object first)
    import json

    # json.loads accepts str, bytes, bytearray but not memoryview
    if isinstance(data, memoryview):
        parsed = json.loads(data.tobytes())
    else:
        parsed = json.loads(data)
    return validate_json(schema, parsed)


def validate_json_cached(schema: dict[str, Any], data: Any) -> dict[str, Any]:
    """Validate data against schema with schema caching.

    For repeated validation against the same schema, this is faster than
    validate_json() because the schema is parsed only once.

    Note: The native CPython extension doesn't currently support schema caching,
    so this function behaves the same as validate_json() when using native backend.

    Args:
        schema: JSON Schema dictionary
        data: Data to validate (already parsed from JSON)

    Returns:
        Dict with "valid" boolean and optionally "errors" list
    """
    # Native backend doesn't support caching yet, just use validate_json
    return validate_json(schema, data)


def _validate_with_jsonschema(schema: dict[str, Any], data: Any) -> dict[str, Any]:
    """Validate using jsonschema library (fallback)."""
    from jsonschema import Draft7Validator, FormatChecker

    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(data))

    if not errors:
        return {"valid": True}

    return {
        "valid": False,
        "errors": [
            {
                "path": _format_path(error.absolute_path),
                "message": error.message,
            }
            for error in errors
        ],
    }


def _format_path(path: Any) -> str:
    """Format JSON path from deque to string."""
    parts = ["$"]
    for part in path:
        if isinstance(part, int):
            parts.append(f"[{part}]")
        else:
            parts.append(f".{part}")
    return "".join(parts)


def get_backend_info() -> dict[str, Any]:
    """Get information about the current validation backend.

    Returns:
        Dict with backend info including:
        - backend: "native" or "jsonschema"
        - native_available: bool
        - native_version: str or None
        - has_heap_types: bool (True if native extension uses heap types)
        - has_buffer_protocol: bool (True if validate_json_bytes is available)
    """
    return {
        "backend": "native" if _native_available else "jsonschema",
        "native_available": _native_available,
        "native_version": _native_version,
        "has_heap_types": _ValidationResult is not None,
        "has_buffer_protocol": _native_validate_bytes is not None,
    }


def parse_yaml(yaml_str: str) -> dict[str, Any]:
    """Parse SlimSchema YAML and return JSON Schema.

    Converts SlimSchema's compact YAML syntax to standard JSON Schema.
    Requires native Zig backend.

    Args:
        yaml_str: SlimSchema YAML definition

    Returns:
        JSON Schema dict compatible with OpenAI, Anthropic, Google function calling

    Raises:
        RuntimeError: If native backend is not available
        ValueError: If YAML parsing fails

    Examples:
        >>> schema = parse_yaml('''
        ... name: str{1..50}
        ... age: 18..120
        ... ?email: email
        ... ''')
        >>> schema["type"]
        'object'
    """
    if not _native_available or _native_parse_yaml is None:
        raise RuntimeError(
            "parse_yaml requires native Zig backend. "
            "Ensure slimschema was built with 'make build'."
        )
    return _native_parse_yaml(yaml_str)


def to_yaml(yaml_str: str, *, min_comment_column: int = 30) -> str:
    """Parse SlimSchema YAML and regenerate with aligned comments.

    Parses the input YAML and outputs it with comments aligned at a
    consistent column position for readability.

    Args:
        yaml_str: SlimSchema YAML definition
        min_comment_column: Minimum column for comment alignment (default 30).
            Comments align at max(field_width + 2, min_comment_column).

    Returns:
        YAML string with aligned comments

    Raises:
        RuntimeError: If native backend is not available
        ValueError: If YAML parsing fails

    Examples:
        >>> print(to_yaml('''
        ... a: str  # short field
        ... username: str  # medium field
        ... very_long_field_name: str  # long field
        ... '''))
        a: str                         # short field
        username: str                  # medium field
        very_long_field_name: str      # long field
    """
    if not _native_available or _native_to_yaml is None:
        raise RuntimeError(
            "to_yaml requires native Zig backend. "
            "Ensure slimschema was built with 'make build'."
        )
    return _native_to_yaml(yaml_str, min_comment_column)


def parse_yaml_safe(
    yaml_str: str,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Parse SlimSchema YAML with error collection mode.

    Unlike parse_yaml() which raises on first error, this function continues
    parsing after recoverable errors and collects all issues. Useful for
    showing all errors to users at once (e.g., in an editor or CI).

    Args:
        yaml_str: SlimSchema YAML definition

    Returns:
        Tuple of (json_schema, errors):
        - json_schema: JSON Schema dict if parsing succeeded, None otherwise
        - errors: List of error dicts with keys: line, column, error_type, message

    Raises:
        RuntimeError: If native backend is not available

    Examples:
        >>> schema, errors = parse_yaml_safe('''
        ... name: str
        ... \tage: int
        ... ''')
        >>> len(errors)
        1
        >>> errors[0]['error_type']
        'tabs_not_allowed'
    """
    if not _native_available or _native_parse_yaml_safe is None:
        raise RuntimeError(
            "parse_yaml_safe requires native Zig backend. "
            "Ensure slimschema was built with 'make build'."
        )
    return _native_parse_yaml_safe(yaml_str)
