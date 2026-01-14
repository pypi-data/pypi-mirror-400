"""Schema class for YAML-based schema definitions.

Provides an object-oriented interface for working with SlimSchema YAML schemas.
This is the primary API for BotAssembly and similar consumers.

Example:
    from slimschema import Schema

    # Parse from YAML
    schema = Schema.from_yaml('''
    name: str{1..50}
    age: 18..120
    ?email: email
    ''')

    # Generate JSON Schema for LLM tool definitions
    json_schema = schema.to_json_schema()

    # Validate data at runtime
    result = schema.validate({"name": "Alice", "age": 30})
    if not result.valid:
        for error in result.errors:
            print(f"{error.path}: {error.message}")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SchemaError:
    """A single error from schema validation or parsing.

    Attributes:
        path: JSON path to the error location (e.g., "$.name", "$.items[0].file")
        error_type: Category of error (e.g., "type_mismatch", "missing_field")
        message: Human-readable error description
        line: Source line number (1-indexed), if available
        column: Source column number (1-indexed), if available
    """

    path: str
    message: str
    error_type: str = "validation_error"
    line: int | None = None
    column: int | None = None


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Result of validating data against a schema.

    Attributes:
        valid: True if validation passed, False otherwise
        errors: List of errors if validation failed, empty list if passed
    """

    valid: bool
    errors: list[SchemaError] = field(default_factory=list)

    def raise_on_error(self) -> None:
        """Raise ValidationError if validation failed.

        Raises:
            ValidationError: If validation was not successful
        """
        if not self.valid:
            from .errors import ValidationError

            error_dicts = [{"path": e.path, "message": e.message} for e in self.errors]
            raise ValidationError(error_dicts)


class Schema:
    """A parsed SlimSchema schema.

    Use the class methods to create Schema instances:
    - Schema.from_yaml(yaml_str) - Parse from SlimSchema YAML syntax
    - Schema.from_dict(d) - Create from already-parsed dict
    - Schema.from_json_schema(schema) - Wrap existing JSON Schema

    Once created, use the instance methods:
    - to_json_schema() - Generate JSON Schema dict
    - validate(data) - Validate data and return ValidationResult
    - validate_json(json_str) - Parse JSON and validate
    """

    def __init__(self, json_schema: dict[str, Any], *, _yaml_source: str | None = None):
        """Create a Schema from JSON Schema dict.

        Prefer using the class methods (from_yaml, from_dict, from_json_schema)
        instead of calling __init__ directly.

        Args:
            json_schema: JSON Schema dictionary
            _yaml_source: Original YAML source (internal use)
        """
        self._json_schema = json_schema
        self._yaml_source = _yaml_source

    @classmethod
    def from_yaml(cls, yaml_str: str) -> Schema:
        """Parse a SlimSchema YAML definition into a Schema object.

        Args:
            yaml_str: SlimSchema YAML definition

        Returns:
            Schema object that can be used for validation and JSON Schema generation

        Raises:
            RuntimeError: If native backend is not available
            ValueError: If YAML parsing fails

        Example:
            schema = Schema.from_yaml('''
            name: str{1..50}
            age: 18..120
            ?email: email
            issues:
              - file: str
                line: int
                message: str
            ''')
        """
        from .backend import parse_yaml

        json_schema = parse_yaml(yaml_str)
        return cls(json_schema, _yaml_source=yaml_str)

    @classmethod
    def from_yaml_safe(cls, yaml_str: str) -> tuple[Schema | None, list[SchemaError]]:
        """Parse YAML and collect all errors instead of raising.

        Unlike from_yaml() which raises on first error, this method continues
        parsing after recoverable errors and collects all issues. Useful for
        showing all errors to users at once (e.g., in an editor or CI).

        Args:
            yaml_str: SlimSchema YAML definition

        Returns:
            Tuple of (schema, errors):
            - If parsing succeeds with no errors: (Schema, [])
            - If parsing fails: (None, [SchemaError, ...])
            - If parsing partially succeeds: (Schema, [SchemaError, ...])

        Example:
            schema, errors = Schema.from_yaml_safe(yaml_str)
            if errors:
                for err in errors:
                    print(f"Line {err.line}: {err.message}")
            elif schema:
                result = schema.validate(data)
        """
        from .backend import parse_yaml_safe

        try:
            json_schema, error_dicts = parse_yaml_safe(yaml_str)
        except RuntimeError as e:
            # Backend not available
            error = SchemaError(
                path="$",
                message=str(e),
                error_type="runtime_error",
            )
            return None, [error]

        # Convert error dicts to SchemaError objects
        errors = []
        for err in error_dicts:
            errors.append(
                SchemaError(
                    path="$",
                    message=err.get("message", "unknown error"),
                    error_type=err.get("error_type", "parse_error"),
                    line=err.get("line"),
                    column=err.get("column"),
                )
            )

        # Create Schema if parsing succeeded
        schema = cls(json_schema, _yaml_source=yaml_str) if json_schema else None

        return schema, errors

    @classmethod
    def from_json_schema(cls, schema: dict[str, Any]) -> Schema:
        """Create a Schema from an existing JSON Schema.

        Use this when you already have a JSON Schema dict and want to
        use SlimSchema's validation capabilities.

        Args:
            schema: JSON Schema dictionary

        Returns:
            Schema object wrapping the JSON Schema
        """
        return cls(schema)

    def to_json_schema(self) -> dict[str, Any]:
        """Generate JSON Schema representation.

        Returns a standard JSON Schema dict suitable for:
        - OpenAI function calling
        - Anthropic tool use
        - Google Gemini function calling
        - Any JSON Schema validator

        Returns:
            JSON Schema dict
        """
        return self._json_schema.copy()

    def to_json_schema_string(self, *, indent: int | None = None) -> str:
        """Generate JSON Schema as a JSON string.

        Args:
            indent: Indentation level for pretty-printing. None for compact.

        Returns:
            JSON string representation of the schema
        """
        return json.dumps(self._json_schema, indent=indent)

    def validate(self, data: Any) -> ValidationResult:
        """Validate data against this schema.

        Args:
            data: Data to validate (Python dict/list, already parsed from JSON)

        Returns:
            ValidationResult with valid=True if passed, or valid=False with errors
        """
        from .backend import validate_json

        result_dict = validate_json(self._json_schema, data)
        return _dict_to_validation_result(result_dict)

    def validate_json(self, json_str: str | bytes) -> ValidationResult:
        """Parse JSON string and validate against this schema.

        This is a convenience method that combines JSON parsing with validation.
        For bytes input, uses the optimized buffer protocol path.

        Args:
            json_str: JSON string or bytes to parse and validate

        Returns:
            ValidationResult with valid=True if passed, or valid=False with errors
        """
        from .backend import validate_json_bytes

        result_dict = validate_json_bytes(self._json_schema, json_str)
        return _dict_to_validation_result(result_dict)

    def validate_or_raise(self, data: Any) -> None:
        """Validate data and raise if invalid.

        Convenience method that validates and raises ValidationError on failure.

        Args:
            data: Data to validate

        Raises:
            ValidationError: If validation fails
        """
        result = self.validate(data)
        result.raise_on_error()

    @property
    def yaml_source(self) -> str | None:
        """Original YAML source, if this schema was parsed from YAML."""
        return self._yaml_source

    def __repr__(self) -> str:
        if self._yaml_source:
            return f"Schema.from_yaml({self._yaml_source[:50]!r}...)"
        return f"Schema({self._json_schema!r})"


def _dict_to_validation_result(result: dict[str, Any]) -> ValidationResult:
    """Convert backend validation result dict to ValidationResult object."""
    if result.get("valid", True):
        return ValidationResult(valid=True)

    errors = []
    for err in result.get("errors", []):
        errors.append(
            SchemaError(
                path=err.get("path", "$"),
                message=err.get("message", "unknown error"),
                error_type=err.get("error_type", "validation_error"),
                line=err.get("line"),
                column=err.get("column"),
            )
        )
    return ValidationResult(valid=False, errors=errors)
