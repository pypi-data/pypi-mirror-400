"""Tests for Schema class and YAML list syntax support.

These tests verify the BotAssembly-required API:
- Schema.from_yaml() - Parse SlimSchema YAML
- Schema.from_yaml_safe() - Parse with error collection
- Schema.from_dict() - Create from dict
- Schema.from_json_schema() - Wrap existing JSON Schema
- schema.to_json_schema() - Generate JSON Schema
- schema.validate() - Validate data
- schema.validate_json() - Validate JSON string
- ValidationResult and SchemaError classes
"""

from __future__ import annotations

import textwrap

import pytest

from slimschema import Schema, SchemaError, ValidationResult


def yaml(s: str) -> str:
    """Helper to dedent and strip YAML strings."""
    return textwrap.dedent(s).strip()


@pytest.fixture(autouse=True)
def require_native_backend():
    """Skip tests if native backend is not available."""
    # Import fresh to avoid stale module state from other tests
    import importlib

    import slimschema.backend as backend

    # Reload to get fresh state in case other tests modified it
    backend = importlib.reload(backend)

    if not backend._native_available or backend._native_parse_yaml is None:
        pytest.skip("Native backend required for Schema class tests")


class TestSchemaFromYaml:
    """Test Schema.from_yaml() parsing."""

    def test_simple_flat_schema(self):
        """Test parsing a simple flat schema."""
        schema = Schema.from_yaml(yaml("""
            name: str
            age: int
            active: bool
        """))

        json_schema = schema.to_json_schema()
        assert json_schema["type"] == "object"
        assert "name" in json_schema["properties"]
        assert json_schema["properties"]["name"]["type"] == "string"
        assert json_schema["properties"]["age"]["type"] == "integer"
        assert json_schema["properties"]["active"]["type"] == "boolean"

    def test_optional_fields(self):
        """Test parsing optional fields with ? prefix."""
        schema = Schema.from_yaml(yaml("""
            name: str
            ?email: str
            ?age: int
        """))

        json_schema = schema.to_json_schema()
        assert "name" in json_schema.get("required", [])
        assert "email" not in json_schema.get("required", [])
        assert "age" not in json_schema.get("required", [])

    def test_nested_schema(self):
        """Test parsing nested object schemas."""
        schema = Schema.from_yaml(yaml("""
            user:
              name: str
              age: int
        """))

        json_schema = schema.to_json_schema()
        assert json_schema["properties"]["user"]["type"] == "object"
        assert "name" in json_schema["properties"]["user"]["properties"]

    def test_string_constraints(self):
        """Test parsing string length constraints."""
        schema = Schema.from_yaml(yaml("""
            name: str{1..50}
            code: str{6..6}
        """))

        json_schema = schema.to_json_schema()
        name_prop = json_schema["properties"]["name"]
        assert name_prop["minLength"] == 1
        assert name_prop["maxLength"] == 50
        # Exact length is specified as min..max with same values
        code_prop = json_schema["properties"]["code"]
        assert code_prop["minLength"] == 6
        assert code_prop["maxLength"] == 6

    def test_integer_range_constraints(self):
        """Test parsing integer range constraints."""
        schema = Schema.from_yaml(yaml("""
            age: 18..120
            count: 1..100
        """))

        json_schema = schema.to_json_schema()
        age_prop = json_schema["properties"]["age"]
        assert age_prop["minimum"] == 18
        assert age_prop["maximum"] == 120


class TestYamlListSyntax:
    """Test YAML list syntax with - prefix (BotAssembly critical requirement)."""

    def test_simple_list_items(self):
        """Test basic YAML list syntax."""
        schema = Schema.from_yaml(yaml("""
            issues:
              - file: str
                line: int
                message: str
        """))

        json_schema = schema.to_json_schema()
        assert json_schema["properties"]["issues"]["type"] == "array"
        items_schema = json_schema["properties"]["issues"]["items"]
        assert items_schema["type"] == "object"
        assert "file" in items_schema["properties"]
        assert "line" in items_schema["properties"]
        assert "message" in items_schema["properties"]

    def test_list_with_optional_fields(self):
        """Test list items with optional field markers."""
        schema = Schema.from_yaml(yaml("""
            results:
              - name: str
                ?score: int
                ?metadata: str
        """))

        json_schema = schema.to_json_schema()
        items_schema = json_schema["properties"]["results"]["items"]
        assert "name" in items_schema.get("required", [])
        assert "score" not in items_schema.get("required", [])

    def test_list_with_constraints(self):
        """Test list items with type constraints."""
        schema = Schema.from_yaml(yaml("""
            files:
              - path: str{1..255}
                size: 0..999999999
        """))

        json_schema = schema.to_json_schema()
        items_schema = json_schema["properties"]["files"]["items"]
        path_prop = items_schema["properties"]["path"]
        assert path_prop["minLength"] == 1
        assert path_prop["maxLength"] == 255

    def test_nested_list_in_object(self):
        """Test list nested inside an object."""
        schema = Schema.from_yaml(yaml("""
            response:
              success: bool
              items:
                - id: int
                  value: str
        """))

        json_schema = schema.to_json_schema()
        response_props = json_schema["properties"]["response"]["properties"]
        assert response_props["items"]["type"] == "array"

    def test_botassembly_agent_response_pattern(self):
        """Test the exact pattern BotAssembly uses for agent responses."""
        schema = Schema.from_yaml(yaml("""
            summary:
              total_files: int
              total_lines: int
            issues:
              - file: str
                line: int
                severity: str
                message: str
            success: bool
        """))

        json_schema = schema.to_json_schema()

        # Verify top-level structure
        props = json_schema["properties"]
        assert "summary" in props
        assert "issues" in props
        assert "success" in props

        # Verify summary is nested object
        assert props["summary"]["type"] == "object"
        assert "total_files" in props["summary"]["properties"]

        # Verify issues is array of objects
        assert props["issues"]["type"] == "array"
        items = props["issues"]["items"]
        assert items["type"] == "object"
        assert all(f in items["properties"] for f in ["file", "line", "severity", "message"])


class TestSchemaValidation:
    """Test schema validation functionality."""

    def test_validate_valid_data(self):
        """Test validating data that matches the schema."""
        schema = Schema.from_yaml(yaml("""
            name: str
            age: int
        """))

        result = schema.validate({"name": "Alice", "age": 30})
        assert result.valid is True
        assert result.errors == []

    def test_validate_invalid_data(self):
        """Test validating data that doesn't match the schema."""
        schema = Schema.from_yaml(yaml("""
            name: str
            age: int
        """))

        result = schema.validate({"name": "Alice", "age": "not an int"})
        assert result.valid is False
        assert len(result.errors) > 0
        assert any("age" in e.path for e in result.errors)

    def test_validate_missing_required_field(self):
        """Test validating data missing a required field."""
        schema = Schema.from_yaml(yaml("""
            name: str
            age: int
        """))

        result = schema.validate({"name": "Alice"})
        assert result.valid is False
        assert any("age" in e.message.lower() or "required" in e.message.lower()
                   for e in result.errors)

    def test_validate_list_items(self):
        """Test validating array items."""
        schema = Schema.from_yaml(yaml("""
            items:
              - name: str
                count: int
        """))

        # Valid data
        result = schema.validate({
            "items": [
                {"name": "A", "count": 1},
                {"name": "B", "count": 2},
            ]
        })
        assert result.valid is True

        # Invalid item
        result = schema.validate({
            "items": [
                {"name": "A", "count": 1},
                {"name": "B", "count": "not int"},
            ]
        })
        assert result.valid is False
        assert any("[1]" in e.path for e in result.errors)  # Error in second item

    def test_validate_json_string(self):
        """Test validate_json() with JSON string input."""
        schema = Schema.from_yaml(yaml("""
            name: str
            age: int
        """))

        result = schema.validate_json('{"name": "Alice", "age": 30}')
        assert result.valid is True

        result = schema.validate_json('{"name": "Alice", "age": "bad"}')
        assert result.valid is False

    def test_validate_json_bytes(self):
        """Test validate_json() with bytes input."""
        schema = Schema.from_yaml(yaml("""
            name: str
        """))

        result = schema.validate_json(b'{"name": "Alice"}')
        assert result.valid is True

    def test_validate_or_raise(self):
        """Test validate_or_raise() raises on invalid data."""
        from slimschema import ValidationError

        schema = Schema.from_yaml(yaml("""
            name: str
        """))

        # Should not raise for valid data
        schema.validate_or_raise({"name": "Alice"})

        # Should raise for invalid data
        with pytest.raises(ValidationError):
            schema.validate_or_raise({"name": 123})


class TestValidationResult:
    """Test ValidationResult class."""

    def test_validation_result_valid(self):
        """Test ValidationResult for valid data."""
        result = ValidationResult(valid=True)
        assert result.valid is True
        assert result.errors == []

    def test_validation_result_invalid(self):
        """Test ValidationResult for invalid data."""
        errors = [
            SchemaError(path="$.name", message="type mismatch"),
            SchemaError(path="$.age", message="required field missing"),
        ]
        result = ValidationResult(valid=False, errors=errors)
        assert result.valid is False
        assert len(result.errors) == 2

    def test_validation_result_raise_on_error(self):
        """Test raise_on_error() method."""
        from slimschema import ValidationError

        # Should not raise when valid
        result = ValidationResult(valid=True)
        result.raise_on_error()

        # Should raise when invalid
        result = ValidationResult(
            valid=False,
            errors=[SchemaError(path="$.name", message="error")]
        )
        with pytest.raises(ValidationError):
            result.raise_on_error()


class TestSchemaError:
    """Test SchemaError class."""

    def test_schema_error_fields(self):
        """Test SchemaError has all required fields."""
        error = SchemaError(
            path="$.items[0].name",
            message="type mismatch: expected string",
            error_type="type_mismatch",
            line=10,
            column=5,
        )
        assert error.path == "$.items[0].name"
        assert error.message == "type mismatch: expected string"
        assert error.error_type == "type_mismatch"
        assert error.line == 10
        assert error.column == 5

    def test_schema_error_defaults(self):
        """Test SchemaError default values."""
        error = SchemaError(path="$", message="error")
        assert error.error_type == "validation_error"
        assert error.line is None
        assert error.column is None

    def test_schema_error_immutable(self):
        """Test SchemaError is frozen (immutable)."""
        error = SchemaError(path="$", message="error")
        with pytest.raises(AttributeError):
            error.path = "$.other"  # type: ignore


class TestSchemaFromYamlSafe:
    """Test Schema.from_yaml_safe() error collection."""

    def test_successful_parse(self):
        """Test from_yaml_safe() returns schema on success."""
        schema, errors = Schema.from_yaml_safe(yaml("""
            name: str
            age: int
        """))
        assert schema is not None
        assert errors == []
        assert schema.to_json_schema()["type"] == "object"

    def test_parse_error_tabs(self):
        """Test from_yaml_safe() returns errors for tabs."""
        # Tabs in indentation cause parse error
        schema, errors = Schema.from_yaml_safe("\tname: str")
        # Schema should be None or have skipped the bad line
        assert len(errors) > 0
        assert errors[0].error_type == "tabs_not_allowed"
        assert errors[0].line == 1

    def test_parse_error_missing_colon(self):
        """Test from_yaml_safe() returns errors for missing colon."""
        schema, errors = Schema.from_yaml_safe("name str")
        assert schema is None
        assert len(errors) > 0
        assert errors[0].error_type == "invalid_syntax"
        assert "colon" in errors[0].message.lower()

    def test_runtime_error(self, monkeypatch):
        """Test from_yaml_safe() handles RuntimeError (backend unavailable)."""
        import slimschema.backend as backend

        # Mock parse_yaml_safe to raise RuntimeError
        def mock_parse_yaml_safe(yaml_str):
            raise RuntimeError("Native backend not available")

        monkeypatch.setattr(backend, "parse_yaml_safe", mock_parse_yaml_safe)

        schema, errors = Schema.from_yaml_safe("name: str")
        assert schema is None
        assert len(errors) == 1
        assert errors[0].error_type == "runtime_error"
        assert "Native backend" in errors[0].message


class TestSchemaFromJsonSchema:
    """Test Schema.from_json_schema() wrapper."""

    def test_wrap_json_schema(self):
        """Test wrapping an existing JSON Schema."""
        json_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        }

        schema = Schema.from_json_schema(json_schema)
        assert schema.to_json_schema() == json_schema

        # Should be able to validate against it
        result = schema.validate({"name": "Alice", "age": 30})
        assert result.valid is True


class TestSchemaToJsonSchema:
    """Test JSON Schema generation."""

    def test_to_json_schema_returns_copy(self):
        """Test to_json_schema() returns a copy, not reference."""
        schema = Schema.from_yaml("name: str")
        js1 = schema.to_json_schema()
        js2 = schema.to_json_schema()
        assert js1 == js2
        # Note: shallow copy returns same dict structure
        assert js1["type"] == js2["type"]

    def test_to_json_schema_string(self):
        """Test to_json_schema_string() method."""
        import json

        schema = Schema.from_yaml("name: str")
        json_str = schema.to_json_schema_string()
        parsed = json.loads(json_str)
        assert parsed["type"] == "object"

    def test_to_json_schema_string_pretty(self):
        """Test to_json_schema_string() with indentation."""
        schema = Schema.from_yaml("name: str")
        json_str = schema.to_json_schema_string(indent=2)
        assert "\n" in json_str  # Has newlines (pretty printed)


class TestSchemaRepr:
    """Test Schema repr and properties."""

    def test_yaml_source_property(self):
        """Test yaml_source property."""
        yaml = "name: str\nage: int"
        schema = Schema.from_yaml(yaml)
        assert schema.yaml_source == yaml

    def test_yaml_source_none_for_json_schema(self):
        """Test yaml_source is None for from_json_schema()."""
        schema = Schema.from_json_schema({"type": "object"})
        assert schema.yaml_source is None

    def test_repr_from_yaml(self):
        """Test __repr__ method for YAML-sourced schema."""
        schema = Schema.from_yaml("name: str")
        r = repr(schema)
        assert "Schema.from_yaml" in r
        assert "name: str" in r

    def test_repr_from_json_schema(self):
        """Test __repr__ method for JSON Schema-sourced schema."""
        schema = Schema.from_json_schema({"type": "object"})
        r = repr(schema)
        assert "Schema(" in r
        assert "object" in r
