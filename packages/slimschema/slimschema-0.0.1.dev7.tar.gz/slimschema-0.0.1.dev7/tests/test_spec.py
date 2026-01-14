"""Tests for @spec decorator - schema generation and dataclass behavior.

Tests that require the Zig backend (parsing) are in test_integration.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID, uuid4

import pytest

from slimschema import (
    Alias,
    Check,
    Date,
    DateTime,
    Email,
    Len,
    Pattern,
    Range,
    Url,
    Uuid,
    ValidationError,
    field_validator,
    model_validator,
    spec,
)


class TestSchemaGeneration:
    """Test JSON Schema generation from @spec classes."""

    def test_basic_types(self):
        """Test schema for basic Python types."""

        @spec
        class User:
            name: str
            age: int
            score: float
            active: bool

        schema = User.json_schema()
        assert schema["type"] == "object"
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["age"]["type"] == "integer"
        assert schema["properties"]["score"]["type"] == "number"
        assert schema["properties"]["active"]["type"] == "boolean"

    def test_required_fields(self):
        """Test required vs optional fields in schema."""

        @spec
        class User:
            name: str
            nickname: str | None = None

        schema = User.json_schema()
        assert "name" in schema["required"]
        assert "nickname" not in schema["required"]

    def test_literal_types(self):
        """Test Literal enum constraint in schema."""

        @spec
        class Task:
            status: Literal["pending", "done", "cancelled"]

        schema = Task.json_schema()
        assert schema["properties"]["status"]["type"] == "string"
        assert schema["properties"]["status"]["enum"] == [
            "pending",
            "done",
            "cancelled",
        ]

    def test_list_types(self):
        """Test list/array types in schema."""

        @spec
        class User:
            tags: list[str]

        schema = User.json_schema()
        assert schema["properties"]["tags"]["type"] == "array"
        assert schema["properties"]["tags"]["items"]["type"] == "string"

    def test_additional_properties_false(self):
        """Test that additionalProperties is set to false."""

        @spec
        class User:
            name: str

        schema = User.json_schema()
        assert schema["additionalProperties"] is False


class TestConstraints:
    """Test constraint types in schema generation."""

    def test_len_string(self):
        """Test Len constraint on strings."""

        @spec
        class User:
            name: Annotated[str, Len(1, 50)]

        schema = User.json_schema()
        assert schema["properties"]["name"]["minLength"] == 1
        assert schema["properties"]["name"]["maxLength"] == 50

    def test_len_zero_minimum(self):
        """Test Len constraint with min=0 is set correctly."""

        @spec
        class User:
            tags: Annotated[list[str], Len(0, 10)]

        schema = User.json_schema()
        assert schema["properties"]["tags"]["minItems"] == 0
        assert schema["properties"]["tags"]["maxItems"] == 10

    def test_len_minimum_only(self):
        """Test Len with only minimum specified."""

        @spec
        class Comment:
            text: Annotated[str, Len(10)]

        schema = Comment.json_schema()
        assert schema["properties"]["text"]["minLength"] == 10
        assert "maxLength" not in schema["properties"]["text"]

    def test_range_integer(self):
        """Test Range constraint on integers."""

        @spec
        class User:
            age: Annotated[int, Range(0, 120)]

        schema = User.json_schema()
        assert schema["properties"]["age"]["minimum"] == 0
        assert schema["properties"]["age"]["maximum"] == 120

    def test_range_float(self):
        """Test Range constraint on floats."""

        @spec
        class Score:
            value: Annotated[float, Range(0.0, 1.0)]

        schema = Score.json_schema()
        assert schema["properties"]["value"]["minimum"] == 0.0
        assert schema["properties"]["value"]["maximum"] == 1.0

    def test_pattern(self):
        """Test Pattern constraint."""

        @spec
        class Code:
            value: Annotated[str, Pattern(r"^[A-Z]{3}$")]

        schema = Code.json_schema()
        assert schema["properties"]["value"]["pattern"] == "^[A-Z]{3}$"

    def test_combined_constraints(self):
        """Test multiple constraints on same field."""

        @spec
        class Code:
            value: Annotated[str, Len(3, 10), Pattern(r"^[A-Z]+$")]

        schema = Code.json_schema()
        assert schema["properties"]["value"]["minLength"] == 3
        assert schema["properties"]["value"]["maxLength"] == 10
        assert schema["properties"]["value"]["pattern"] == "^[A-Z]+$"


class TestFormats:
    """Test format markers in schema generation."""

    def test_email_format(self):
        """Test Email format marker."""

        @spec
        class User:
            email: Annotated[str, Email]

        schema = User.json_schema()
        assert schema["properties"]["email"]["format"] == "email"

    def test_url_format(self):
        """Test Url format marker."""

        @spec
        class Link:
            href: Annotated[str, Url]

        schema = Link.json_schema()
        assert schema["properties"]["href"]["format"] == "uri"

    def test_uuid_format(self):
        """Test Uuid format marker."""

        @spec
        class Entity:
            id: Annotated[str, Uuid]

        schema = Entity.json_schema()
        assert schema["properties"]["id"]["format"] == "uuid"

    def test_date_format(self):
        """Test Date format marker."""

        @spec
        class Event:
            date: Annotated[str, Date]

        schema = Event.json_schema()
        assert schema["properties"]["date"]["format"] == "date"

    def test_datetime_format(self):
        """Test DateTime format marker."""

        @spec
        class Event:
            timestamp: Annotated[str, DateTime]

        schema = Event.json_schema()
        assert schema["properties"]["timestamp"]["format"] == "date-time"


class TestAliases:
    """Test field alias support in schema generation."""

    def test_alias_in_schema(self):
        """Test that aliases become JSON property names."""

        @spec
        class User:
            user_name: Annotated[str, Alias("userName")]

        schema = User.json_schema()
        assert "userName" in schema["properties"]
        assert "user_name" not in schema["properties"]

    def test_alias_with_constraints(self):
        """Test alias combined with other constraints."""

        @spec
        class User:
            user_name: Annotated[str, Alias("userName"), Len(1, 50)]

        schema = User.json_schema()
        assert "userName" in schema["properties"]
        assert schema["properties"]["userName"]["minLength"] == 1

    def test_alias_in_required(self):
        """Test that required list uses alias names."""

        @spec
        class User:
            user_name: Annotated[str, Alias("userName")]

        schema = User.json_schema()
        assert "userName" in schema["required"]


class TestValidationError:
    """Test ValidationError class."""

    def test_error_message_format(self):
        """Test ValidationError formats message correctly."""
        error = ValidationError(
            [
                {"path": "$.name", "message": "too short"},
                {"path": "$.age", "message": "too large"},
            ]
        )
        message = str(error)
        assert "$.name: too short" in message
        assert "$.age: too large" in message

    def test_error_attributes(self):
        """Test ValidationError stores errors list."""
        errors = [{"path": "$.name", "message": "invalid"}]
        error = ValidationError(errors)
        assert error.errors == errors

    def test_error_with_msg_key(self):
        """Test ValidationError handles 'msg' key as well as 'message'."""
        error = ValidationError([{"path": "$.x", "msg": "bad value"}])
        assert "bad value" in str(error)


class TestDataclassBehavior:
    """Test that @spec creates proper dataclasses."""

    def test_slots_default_true(self):
        """Test slots=True is the default (memory efficient)."""

        @spec
        class Point:
            x: float = 0.0
            y: float = 0.0

        p = Point(x=1.0, y=2.0)
        assert not hasattr(p, "__dict__")

    def test_frozen_option(self):
        """Test frozen=True creates immutable instances."""

        @spec(frozen=True)
        class Config:
            host: str = "localhost"

        config = Config(host="example.com")

        with pytest.raises(AttributeError):
            config.host = "newhost"  # type: ignore

    def test_equality(self):
        """Test dataclass equality works."""

        @spec
        class Point:
            x: float = 0.0
            y: float = 0.0

        p1 = Point(x=1.0, y=2.0)
        p2 = Point(x=1.0, y=2.0)
        p3 = Point(x=3.0, y=4.0)

        assert p1 == p2
        assert p1 != p3

    def test_repr(self):
        """Test dataclass repr works."""

        @spec
        class Point:
            x: float = 0.0
            y: float = 0.0

        p = Point(x=1.0, y=2.0)
        assert "Point" in repr(p)
        assert "x=1.0" in repr(p)
        assert "y=2.0" in repr(p)

    def test_default_values(self):
        """Test fields with default values work."""

        @spec
        class Config:
            host: str = "localhost"
            port: int = 8080

        config = Config()
        assert config.host == "localhost"
        assert config.port == 8080


class TestAdvancedSchemaGeneration:
    """Test schema generation for advanced type hints."""

    def test_union_optional_uses_anyof(self):
        @spec
        class User:
            nickname: str | None = None

        schema = User.json_schema()
        any_of = schema["properties"]["nickname"]["anyOf"]
        assert {s.get("type") for s in any_of} == {"string", "null"}

    def test_union_multiple_types(self):
        @spec
        class Value:
            value: int | str

        schema = Value.json_schema()
        any_of = schema["properties"]["value"]["anyOf"]
        assert {s.get("type") for s in any_of} == {"integer", "string"}

    def test_union_with_none_and_multiple_types(self):
        @spec
        class MaybeValue:
            value: int | str | None

        schema = MaybeValue.json_schema()
        any_of = schema["properties"]["value"]["anyOf"]
        assert {s.get("type") for s in any_of} == {"integer", "string", "null"}

    def test_dict_schema_with_value_type(self):
        @spec
        class Scores:
            scores: dict[str, int]

        schema = Scores.json_schema()
        prop = schema["properties"]["scores"]
        assert prop["type"] == "object"
        assert prop["additionalProperties"]["type"] == "integer"

    def test_nested_spec_schema_is_not_mutated_by_optional(self):
        @spec
        class Address:
            street: str

        globals()["Address"] = Address
        try:
            @spec
            class User:
                address: Address | None = None
        finally:
            del globals()["Address"]

        assert "anyOf" not in Address.json_schema()
        user_schema = User.json_schema()
        assert "anyOf" in user_schema["properties"]["address"]


class TestParsingAndValidationFeatures:
    """Test parsing helpers and Python-side validation features."""

    def test_native_types_with_default_factory(self):
        """Test native UUID and datetime types with default_factory."""

        @spec
        class Event:
            id: UUID = field(default_factory=uuid4)
            created: datetime = field(default_factory=datetime.now)

        e1 = Event()
        e2 = Event()
        assert isinstance(e1.id, UUID)
        assert isinstance(e1.created, datetime)
        assert e1.id != e2.id

        # Check schema generation
        schema = Event.json_schema()
        assert schema["properties"]["id"] == {"type": "string", "format": "uuid"}
        assert schema["properties"]["created"] == {
            "type": "string",
            "format": "date-time",
        }

    def test_check_repr(self):
        def no_op(v: str) -> str:
            return v

        assert repr(Check(no_op)) == "Check(no_op)"

    def test_loads_multiple(self):
        @spec
        class User:
            name: str

        users = [User.loads(s) for s in ['{"name":"a"}', '{"name":"b"}']]
        assert [u.name for u in users] == ["a", "b"]

    def test_load_with_alias_and_coerce(self):
        @spec(coerce=True)
        class User:
            user_name: Annotated[str, Alias("userName")]
            age: int

        user = User.load({"userName": "alice", "age": "30"})
        assert user.user_name == "alice"
        assert user.age == 30
        assert isinstance(user.age, int)

    def test_nested_instantiation_and_optional(self):
        @spec
        class Address:
            street: str

        globals()["Address"] = Address
        try:
            @spec
            class User:
                address: Address
                addresses: list[Address]
                maybe: Address | None = None
        finally:
            del globals()["Address"]

        u1 = User.load(
            {
                "address": {"street": "main"},
                "addresses": [{"street": "a"}, {"street": "b"}],
                "maybe": None,
            }
        )
        assert isinstance(u1.address, Address)
        assert isinstance(u1.addresses[0], Address)
        assert u1.maybe is None

        u2 = User.load(
            {
                "address": {"street": "main"},
                "addresses": [],
                "maybe": {"street": "side"},
            }
        )
        assert isinstance(u2.maybe, Address)

    def test_internal_instantiate_nested_preserves_unknown_keys(self):
        from slimschema.spec import _instantiate_nested

        @spec
        class User:
            name: str

        data = {"name": "alice", "extra": 1}
        assert _instantiate_nested(User, data) == data

    def test_python_validators_run_and_raise_validation_error(self):
        def no_admin(v: str) -> str:
            if v.lower() == "admin":
                raise ValueError("cannot be admin")
            return v

        globals()["no_admin"] = no_admin
        try:
            @spec
            class User:
                name: Annotated[str, Check(no_admin)]
                role: str

                @field_validator("name")
                @classmethod
                def normalize_name(cls, v: str) -> str:
                    return v.strip()

                @field_validator("role")
                def validate_role(v: str) -> str:
                    if not isinstance(v, str):
                        raise TypeError("role must be a string")
                    v = v.upper()
                    if v not in {"USER", "ADMIN"}:
                        raise ValueError("invalid role")
                    return v

                @model_validator
                @classmethod
                def check_name_not_root(cls, values: dict) -> dict:
                    if values.get("name") == "root":
                        raise ValueError("name cannot be root")
                    return values

                @model_validator
                def check_role_not_banned(values: dict) -> dict:
                    if values.get("role") == "BANNED":
                        raise TypeError("role cannot be banned")
                    return values
        finally:
            del globals()["no_admin"]

        ok = User.load({"name": " alice ", "role": "user"})
        assert ok.name == "alice"
        assert ok.role == "USER"

        with pytest.raises(ValidationError) as exc1:
            User.load({"name": "admin", "role": "user"})
        assert exc1.value.errors[0]["path"] == "$.name"

        with pytest.raises(ValidationError) as exc2:
            User.load({"name": "alice", "role": "hacker"})
        assert exc2.value.errors[0]["path"] == "$.role"

        with pytest.raises(ValidationError) as exc3:
            User.load({"name": "root", "role": "user"})
        assert exc3.value.errors[0]["path"] == "$"


class TestSerialization:
    """Test dump/dumps serialization methods."""

    def test_dump_basic(self):
        """Test dump() returns dict."""

        @spec
        class User:
            name: str
            age: int

        user = User(name="Alice", age=30)
        data = user.dump()

        assert data == {"name": "Alice", "age": 30}
        assert isinstance(data, dict)

    def test_dumps_basic(self):
        """Test dumps() returns JSON string."""

        @spec
        class User:
            name: str
            age: int

        user = User(name="Alice", age=30)
        json_str = user.dumps()

        assert '"name": "Alice"' in json_str or '"name":"Alice"' in json_str
        assert '"age": 30' in json_str or '"age":30' in json_str

    def test_dump_with_alias(self):
        """Test dump() uses JSON aliases."""

        @spec
        class User:
            user_name: Annotated[str, Alias("userName")]
            age: int

        user = User(user_name="Alice", age=30)
        data = user.dump()

        assert data == {"userName": "Alice", "age": 30}
        assert "user_name" not in data

    def test_roundtrip_loads_dumps(self):
        """Test loads -> dumps -> loads roundtrip."""

        @spec
        class User:
            name: str
            age: int

        original = '{"name": "Alice", "age": 30}'
        user = User.loads(original)
        json_str = user.dumps()
        user2 = User.loads(json_str)

        assert user == user2
        assert user2.name == "Alice"
        assert user2.age == 30

    def test_roundtrip_with_alias(self):
        """Test roundtrip with aliases preserves data."""

        @spec
        class User:
            user_name: Annotated[str, Alias("userName")]
            age: int

        original = '{"userName": "Alice", "age": 30}'
        user = User.loads(original)
        json_str = user.dumps()
        user2 = User.loads(json_str)

        assert user == user2
        assert user2.user_name == "Alice"

    def test_dump_with_optional_none(self):
        """Test dump() with None optional field."""

        @spec
        class User:
            name: str
            nickname: str | None = None

        user = User(name="Alice")
        data = user.dump()

        assert data == {"name": "Alice", "nickname": None}


class TestInternalHelpers:
    """Tests for internal helpers used by @spec."""

    def test_extract_schema_without_hints(self):
        from slimschema.spec import _extract_schema

        @dataclass
        class User:
            name: str

        schema = _extract_schema(User)
        assert schema["properties"]["name"]["type"] == "string"

    def test_alias_map_without_hints(self):
        from slimschema.spec import _get_alias_map

        @dataclass
        class User:
            user_name: Annotated[str, Alias("userName")]

        json_to_field, field_to_json = _get_alias_map(User)
        assert json_to_field == {"userName": "user_name"}
        assert field_to_json == {"user_name": "userName"}

    def test_get_validators_without_hints(self):
        from slimschema.spec import _get_validators

        @dataclass
        class User:
            name: Annotated[str, Check(lambda v: v)]

        field_checks, field_validators, model_validators = _get_validators(User)
        assert "name" in field_checks
        assert field_validators == []
        assert model_validators == []

    def test_instantiate_nested_without_meta_hints(self):
        from slimschema.spec import _instantiate_nested

        @dataclass
        class User:
            age: int

        data = {"age": 1, "extra": 2}
        assert _instantiate_nested(User, data) == data

    def test_convert_nested_value_refreshes_union_args(self, monkeypatch):
        import importlib

        spec_mod = importlib.import_module("slimschema.spec")

        original_get_args = spec_mod.get_args
        call_count = {"n": 0}

        def fake_get_args(hint):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return ()
            return original_get_args(hint)

        monkeypatch.setattr(spec_mod, "get_args", fake_get_args)
        assert spec_mod._convert_nested_value(int | None, 1) == 1

    def test_unknown_type_hint_schema_is_empty(self):
        @spec
        class Weird:
            tags: set[str]

        schema = Weird.json_schema()
        assert schema["properties"]["tags"] == {}
