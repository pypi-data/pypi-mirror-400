"""Tests for type coercion module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import pytest

from slimschema import Alias, Len, Range, spec
from slimschema.coerce import _get_base_type, coerce_data, coerce_value


class TestCoerceValue:
    """Test coerce_value function."""

    def test_string_to_int(self):
        """Test coercing string to int."""
        assert coerce_value("42", int) == 42
        assert coerce_value("-10", int) == -10

    def test_float_to_int(self):
        """Test coercing float to int."""
        assert coerce_value(3.14, int) == 3
        assert coerce_value(3.9, int) == 3

    def test_string_to_float(self):
        """Test coercing string to float."""
        assert coerce_value("3.14", float) == 3.14
        assert coerce_value("-2.5", float) == -2.5

    def test_int_to_float(self):
        """Test coercing int to float."""
        assert coerce_value(42, float) == 42.0

    def test_string_to_bool_true(self):
        """Test coercing truthy strings to bool."""
        assert coerce_value("true", bool) is True
        assert coerce_value("True", bool) is True
        assert coerce_value("TRUE", bool) is True
        assert coerce_value("1", bool) is True
        assert coerce_value("yes", bool) is True
        assert coerce_value("on", bool) is True

    def test_string_to_bool_false(self):
        """Test coercing falsy strings to bool."""
        assert coerce_value("false", bool) is False
        assert coerce_value("False", bool) is False
        assert coerce_value("0", bool) is False
        assert coerce_value("no", bool) is False
        assert coerce_value("", bool) is False

    def test_int_to_bool(self):
        """Test coercing int to bool."""
        assert coerce_value(1, bool) is True
        assert coerce_value(0, bool) is False
        assert coerce_value(42, bool) is True

    def test_any_to_string(self):
        """Test coercing various types to string."""
        assert coerce_value(42, str) == "42"
        assert coerce_value(3.14, str) == "3.14"
        assert coerce_value(True, str) == "True"

    def test_already_correct_type(self):
        """Test that values already of correct type are returned unchanged."""
        assert coerce_value(42, int) == 42
        assert coerce_value("hello", str) == "hello"
        assert coerce_value(True, bool) is True

    def test_invalid_coercion_raises(self):
        """Test that invalid coercions raise TypeError."""
        with pytest.raises(TypeError):
            coerce_value("not a number", int)

        with pytest.raises(TypeError):
            coerce_value("abc", float)

    def test_unsupported_value_type_raises(self):
        """Test that non-convertible types raise TypeError."""
        with pytest.raises(TypeError):
            coerce_value(["1"], int)


class TestCoerceData:
    """Test coerce_data function with @spec classes."""

    def test_coerce_string_to_int(self):
        """Test coercing string fields to int."""

        @spec
        class User:
            age: int

        data = {"age": "30"}
        result = coerce_data(data, User)
        assert result["age"] == 30
        assert isinstance(result["age"], int)

    def test_coerce_string_to_float(self):
        """Test coercing string fields to float."""

        @spec
        class Measurement:
            value: float

        data = {"value": "3.14"}
        result = coerce_data(data, Measurement)
        assert result["value"] == 3.14

    def test_coerce_string_to_bool(self):
        """Test coercing string fields to bool."""

        @spec
        class Config:
            enabled: bool

        data = {"enabled": "true"}
        result = coerce_data(data, Config)
        assert result["enabled"] is True

    def test_coerce_with_constraints(self):
        """Test coercion works with constrained fields."""

        @spec
        class User:
            age: Annotated[int, Range(0, 120)]

        data = {"age": "25"}
        result = coerce_data(data, User)
        assert result["age"] == 25

    def test_coerce_optional_field(self):
        """Test coercion of optional fields."""

        @spec
        class User:
            age: int | None = None

        data = {"age": "30"}
        result = coerce_data(data, User)
        assert result["age"] == 30

    def test_coerce_missing_field_unchanged(self):
        """Test that missing fields are not affected."""

        @spec
        class User:
            name: str
            age: int = 0

        data = {"name": "Alice"}
        result = coerce_data(data, User)
        assert result == {"name": "Alice"}

    def test_coerce_list_items(self):
        """Test coercing items within a list."""

        @spec
        class Data:
            values: list[int]

        data = {"values": ["1", "2", "3"]}
        result = coerce_data(data, Data)
        assert result["values"] == [1, 2, 3]

    def test_coerce_list_with_constraint(self):
        """Test coercing list items with Len constraint."""

        @spec
        class Data:
            tags: Annotated[list[str], Len(0, 10)]

        data = {"tags": [1, 2, 3]}
        result = coerce_data(data, Data)
        assert result["tags"] == ["1", "2", "3"]

    def test_invalid_coercion_passes_through(self):
        """Test that invalid coercions pass through for validation to catch."""

        @spec
        class User:
            age: int

        data = {"age": "not a number"}
        result = coerce_data(data, User)
        # Invalid value passes through - validation will catch it
        assert result["age"] == "not a number"

    def test_coerce_with_alias_map(self):
        """Test coercion can find values by alias key."""

        @spec
        class User:
            user_name: Annotated[str, Alias("userName")]
            age: int

        data = {"userName": "alice", "age": "30"}
        alias_map = User._slimschema["json_to_field"]  # type: ignore[attr-defined]
        result = coerce_data(data, User, alias_map=alias_map)
        assert result["age"] == 30

    def test_coerce_skips_unhandled_types(self):
        """Test coercion skips fields with unsupported types."""

        @spec
        class User:
            meta: dict[str, int]

        data = {"meta": {"a": 1}}
        assert coerce_data(data, User) == data


def test_get_base_type_handles_empty_union_args(monkeypatch):
    import slimschema.coerce as coerce_mod

    monkeypatch.setattr(coerce_mod, "get_args", lambda _hint: ())
    assert _get_base_type(int | None) is None


def test_coerce_data_falls_back_to_get_type_hints_when_no_meta():
    @dataclass
    class User:
        age: int

    assert coerce_data({"age": "30"}, User) == {"age": 30}
