"""Tests for Pydantic adapter.

These tests require pydantic to be installed.
"""

from __future__ import annotations

import builtins
from dataclasses import field
from typing import Annotated
from uuid import UUID, uuid4

import pytest

from slimschema import Alias, Len, Pattern, Range, spec
from slimschema import to_pydantic as to_pydantic_top
from slimschema.adapters.pydantic import to_pydantic

pydantic = pytest.importorskip("pydantic")


class TestToPydantic:
    """Test to_pydantic conversion function."""

    def test_basic_conversion(self):
        """Test converting a basic @spec class."""

        @spec
        class User:
            name: str
            age: int

        user_model = to_pydantic(User)

        # Verify it's a Pydantic model
        assert issubclass(user_model, pydantic.BaseModel)

        # Verify it can validate data
        user = user_model(name="Alice", age=30)
        assert user.name == "Alice"
        assert user.age == 30

    def test_with_len_constraint(self):
        """Test conversion with Len constraint."""

        @spec
        class User:
            name: Annotated[str, Len(1, 50)]

        user_model = to_pydantic(User)

        # Valid data works
        user = user_model(name="Alice")
        assert user.name == "Alice"

        # Too short fails
        with pytest.raises(pydantic.ValidationError):
            user_model(name="")

    def test_with_len_zero_minimum(self):
        """Test that Len(0, 10) correctly sets min_length=0."""

        @spec
        class Data:
            tags: Annotated[list[str], Len(0, 10)]

        data_model = to_pydantic(Data)

        # Empty list should be valid with min=0
        data = data_model(tags=[])
        assert data.tags == []

    def test_with_range_constraint(self):
        """Test conversion with Range constraint."""

        @spec
        class User:
            age: Annotated[int, Range(0, 120)]

        user_model = to_pydantic(User)

        # Valid range works
        user = user_model(age=30)
        assert user.age == 30

        # Out of range fails
        with pytest.raises(pydantic.ValidationError):
            user_model(age=-1)

        with pytest.raises(pydantic.ValidationError):
            user_model(age=200)

    def test_with_pattern_constraint(self):
        """Test conversion with Pattern constraint."""

        @spec
        class Code:
            value: Annotated[str, Pattern(r"^[A-Z]{3}$")]

        code_model = to_pydantic(Code)

        # Valid pattern works
        code = code_model(value="ABC")
        assert code.value == "ABC"

        # Invalid pattern fails
        with pytest.raises(pydantic.ValidationError):
            code_model(value="abc")

    def test_with_alias(self):
        """Test conversion with Alias."""

        @spec
        class User:
            user_name: Annotated[str, Alias("userName")]

        user_model = to_pydantic(User)

        # Can use alias
        user = user_model(userName="alice")
        assert user.user_name == "alice"

    def test_with_default_values(self):
        """Test conversion with default values."""

        @spec
        class Config:
            host: str = "localhost"
            port: int = 8080

        config_model = to_pydantic(Config)

        # Defaults work
        config = config_model()
        assert config.host == "localhost"
        assert config.port == 8080

        # Override works
        config2 = config_model(host="example.com", port=443)
        assert config2.host == "example.com"
        assert config2.port == 443

    def test_with_default_factory(self):
        """Test conversion with default_factory fields."""

        @spec
        class User:
            id: UUID = field(default_factory=uuid4)

        user_model = to_pydantic(User)
        u1 = user_model()
        u2 = user_model()
        assert isinstance(u1.id, (str, UUID))  # Pydantic may keep as string
        assert u1.id != u2.id
        assert user_model.model_fields["id"].default_factory is not None

    def test_top_level_to_pydantic_proxy(self):
        """Test slimschema.to_pydantic calls the adapter."""

        @spec
        class User:
            name: str

        user_model = to_pydantic_top(User)
        assert issubclass(user_model, pydantic.BaseModel)

    def test_with_optional_field(self):
        """Test conversion with optional field."""

        @spec
        class User:
            name: str
            nickname: str | None = None

        user_model = to_pydantic(User)

        user = user_model(name="Alice")
        assert user.name == "Alice"
        assert user.nickname is None

    def test_non_spec_class_raises(self):
        """Test that non-@spec class raises ValueError."""

        class NotSpec:
            name: str

        with pytest.raises(ValueError) as exc:
            to_pydantic(NotSpec)

        assert "not a @spec class" in str(exc.value)

    def test_missing_pydantic_raises_import_error(self, monkeypatch):
        from slimschema.adapters import pydantic as adapter

        orig_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "pydantic":
                raise ImportError("blocked")
            return orig_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", fake_import)

        @spec
        class User:
            name: str

        with pytest.raises(ImportError) as exc:
            adapter.to_pydantic(User)
        assert "pydantic is required" in str(exc.value)

    def test_combined_constraints(self):
        """Test conversion with multiple constraints."""

        @spec
        class User:
            name: Annotated[str, Len(1, 50), Pattern(r"^[A-Za-z]+$")]

        user_model = to_pydantic(User)

        # Valid
        user = user_model(name="Alice")
        assert user.name == "Alice"

        # Too short
        with pytest.raises(pydantic.ValidationError):
            user_model(name="")

        # Invalid pattern
        with pytest.raises(pydantic.ValidationError):
            user_model(name="Alice123")
