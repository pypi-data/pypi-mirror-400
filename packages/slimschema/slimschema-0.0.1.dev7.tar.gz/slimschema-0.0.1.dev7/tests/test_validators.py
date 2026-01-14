"""Tests for validator decorators."""

from __future__ import annotations

from slimschema.validators import field_validator, model_validator


class TestFieldValidator:
    """Test @field_validator decorator."""

    def test_decorator_marks_function(self):
        """Test that decorator adds _validate_fields attribute."""

        @field_validator("name")
        def validate_name(v: str) -> str:
            return v.upper()

        assert hasattr(validate_name, "_validate_fields")
        assert validate_name._validate_fields == ("name",)

    def test_multiple_fields(self):
        """Test decorator with multiple field names."""

        @field_validator("first", "last")
        def validate_names(v: str) -> str:
            return v.strip()

        assert validate_names._validate_fields == ("first", "last")

    def test_decorator_preserves_function(self):
        """Test that decorated function still works."""

        @field_validator("name")
        def validate_name(v: str) -> str:
            return v.upper()

        assert validate_name("alice") == "ALICE"


class TestModelValidator:
    """Test @model_validator decorator."""

    def test_decorator_marks_function(self):
        """Test that decorator adds _validate_model attribute."""

        @model_validator
        def validate_model(values: dict) -> dict:
            return values

        assert hasattr(validate_model, "_validate_model")
        assert validate_model._validate_model is True

    def test_decorator_preserves_function(self):
        """Test that decorated function still works."""

        @model_validator
        def validate_model(values: dict) -> dict:
            values["processed"] = True
            return values

        result = validate_model({"name": "Alice"})
        assert result == {"name": "Alice", "processed": True}
