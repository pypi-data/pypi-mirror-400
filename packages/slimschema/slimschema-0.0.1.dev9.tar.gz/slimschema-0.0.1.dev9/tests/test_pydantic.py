"""Tests for Pydantic adapter.

These tests require pydantic to be installed.
"""

from __future__ import annotations

import builtins
from dataclasses import field
from typing import Annotated
from uuid import UUID, uuid4

import pytest

from slimschema import Alias, Len, Pattern, Range, Schema, spec
from slimschema import from_pydantic as from_pydantic_top
from slimschema import to_pydantic as to_pydantic_top
from slimschema.adapters.pydantic import from_pydantic, to_pydantic

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


class TestFromPydantic:
    """Test from_pydantic conversion function."""

    def test_basic_conversion(self):
        """Test converting a basic Pydantic model returns a Schema."""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int

        schema = from_pydantic(User)

        # Verify it returns a Schema object
        assert isinstance(schema, Schema)

        # Verify Schema has expected methods
        assert hasattr(schema, "validate")
        assert hasattr(schema, "validate_json")
        assert hasattr(schema, "to_json_schema")

        # Verify it can validate data
        result = schema.validate({"name": "Alice", "age": 30})
        assert result.valid

    def test_validate_json_string(self):
        """Test validating a JSON string."""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int

        schema = from_pydantic(User)
        result = schema.validate_json('{"name": "Bob", "age": 25}')
        assert result.valid

    def test_with_field_constraints(self):
        """Test conversion with Pydantic Field constraints."""
        from pydantic import BaseModel, Field

        class User(BaseModel):
            name: str = Field(min_length=1, max_length=50)
            age: int = Field(ge=0, le=120)

        schema = from_pydantic(User)

        # Valid data works
        result = schema.validate({"name": "Alice", "age": 30})
        assert result.valid

        # Too short name fails
        result = schema.validate({"name": "", "age": 30})
        assert not result.valid

        # Age out of range fails
        result = schema.validate({"name": "Alice", "age": 200})
        assert not result.valid

    def test_with_pattern_constraint(self):
        """Test conversion with pattern constraint."""
        from pydantic import BaseModel, Field

        class Code(BaseModel):
            value: str = Field(pattern=r"^[A-Z]{3}$")

        schema = from_pydantic(Code)

        # Valid pattern works
        result = schema.validate({"value": "ABC"})
        assert result.valid

        # Invalid pattern fails
        result = schema.validate({"value": "abc"})
        assert not result.valid

    def test_with_nested_model(self):
        """Test conversion with nested Pydantic models."""
        from pydantic import BaseModel

        class Address(BaseModel):
            street: str
            city: str

        class User(BaseModel):
            name: str
            address: Address

        schema = from_pydantic(User)

        result = schema.validate({
            "name": "Alice",
            "address": {"street": "123 Main St", "city": "NYC"}
        })
        assert result.valid

    def test_with_optional_field(self):
        """Test conversion with optional field."""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            nickname: str | None = None

        schema = from_pydantic(User)

        # Without optional field
        result = schema.validate({"name": "Alice"})
        assert result.valid

        # With optional field
        result = schema.validate({"name": "Bob", "nickname": "Bobby"})
        assert result.valid

    def test_with_list_field(self):
        """Test conversion with list field."""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            tags: list[str]

        schema = from_pydantic(User)

        result = schema.validate({"name": "Alice", "tags": ["admin", "user"]})
        assert result.valid

    def test_to_json_schema_method(self):
        """Test that to_json_schema() returns the schema."""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int

        schema = from_pydantic(User)
        json_schema = schema.to_json_schema()

        assert json_schema["type"] == "object"
        assert "name" in json_schema["properties"]
        assert "age" in json_schema["properties"]

    def test_non_pydantic_class_raises(self):
        """Test that non-Pydantic class raises ValueError."""

        class NotPydantic:
            name: str

        with pytest.raises(ValueError) as exc:
            from_pydantic(NotPydantic)

        assert "not a Pydantic BaseModel" in str(exc.value)

    def test_top_level_from_pydantic_proxy(self):
        """Test slimschema.from_pydantic calls the adapter."""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str

        schema = from_pydantic_top(User)
        assert isinstance(schema, Schema)

    def test_missing_pydantic_raises_import_error(self, monkeypatch):
        """Test ImportError when pydantic is not installed."""
        from slimschema.adapters import pydantic as adapter

        orig_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "pydantic":
                raise ImportError("blocked")
            return orig_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", fake_import)

        class FakeModel:
            pass

        with pytest.raises(ImportError) as exc:
            adapter.from_pydantic(FakeModel)
        assert "pydantic is required" in str(exc.value)

    def test_invalid_data_type(self):
        """Test validation fails for wrong types."""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int

        schema = from_pydantic(User)

        # String instead of int should fail
        result = schema.validate({"name": "Alice", "age": "thirty"})
        assert not result.valid

    def test_missing_required_field(self):
        """Test validation fails for missing required fields."""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int

        schema = from_pydantic(User)

        result = schema.validate({"name": "Alice"})
        assert not result.valid

    def test_recursive_model(self):
        """Test that recursive models don't cause infinite recursion."""
        from pydantic import BaseModel

        class TreeNode(BaseModel):
            value: str
            children: list[TreeNode] = []

        # This should not raise RecursionError
        schema = from_pydantic(TreeNode)

        # Should be able to validate simple data
        result = schema.validate({"value": "root", "children": []})
        assert result.valid

        # Should work with nested children
        result = schema.validate({
            "value": "parent",
            "children": [
                {"value": "child1", "children": []},
                {"value": "child2", "children": []}
            ]
        })
        assert result.valid


class TestResolveRefs:
    """Test _resolve_refs function for JSON Schema reference resolution."""

    def test_resolve_defs_format(self):
        """Test resolution of $defs format (Pydantic v2)."""
        from slimschema.adapters.pydantic import _resolve_refs

        schema = {
            "type": "object",
            "properties": {
                "address": {"$ref": "#/$defs/Address"}
            },
            "$defs": {
                "Address": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    }
                }
            }
        }

        resolved = _resolve_refs(schema)
        # $defs should be removed after inlining
        assert "$defs" not in resolved
        # Reference should be inlined
        assert resolved["properties"]["address"]["type"] == "object"
        assert resolved["properties"]["address"]["properties"]["city"]["type"] == "string"

    def test_resolve_definitions_format(self):
        """Test resolution of definitions format (Pydantic v1 / older JSON Schema).

        This covers lines 233-234 in pydantic.py which handle the older
        #/definitions/ format used by Pydantic v1 for backwards compatibility.
        """
        from slimschema.adapters.pydantic import _resolve_refs

        # Simulate older Pydantic v1 style schema with #/definitions/
        schema = {
            "type": "object",
            "properties": {
                "address": {"$ref": "#/definitions/Address"},
                "billing": {"$ref": "#/definitions/Address"}
            },
            "definitions": {
                "Address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"}
                    },
                    "required": ["street", "city"]
                }
            }
        }

        resolved = _resolve_refs(schema)
        # definitions should be removed after inlining
        assert "definitions" not in resolved
        # References should be inlined
        assert resolved["properties"]["address"]["type"] == "object"
        assert resolved["properties"]["address"]["properties"]["street"]["type"] == "string"
        assert resolved["properties"]["billing"]["type"] == "object"
        assert resolved["properties"]["billing"]["properties"]["city"]["type"] == "string"

    def test_resolve_unknown_ref_format(self):
        """Test that unknown ref formats are left intact.

        This covers line 243 in pydantic.py - the fallback when a $ref
        doesn't match known patterns (#/$defs/ or #/definitions/).
        """
        from slimschema.adapters.pydantic import _resolve_refs

        # Unknown ref format should be left unchanged
        schema = {
            "type": "object",
            "properties": {
                "external": {"$ref": "https://example.com/schema.json#/Foo"},
                "unknown": {"$ref": "#/components/schemas/Bar"}
            }
        }

        resolved = _resolve_refs(schema)
        # Unknown refs should remain intact
        assert resolved["properties"]["external"]["$ref"] == "https://example.com/schema.json#/Foo"
        assert resolved["properties"]["unknown"]["$ref"] == "#/components/schemas/Bar"

    def test_resolve_no_defs(self):
        """Test that schemas without $defs or definitions pass through unchanged."""
        from slimschema.adapters.pydantic import _resolve_refs

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }

        resolved = _resolve_refs(schema)
        assert resolved == schema
