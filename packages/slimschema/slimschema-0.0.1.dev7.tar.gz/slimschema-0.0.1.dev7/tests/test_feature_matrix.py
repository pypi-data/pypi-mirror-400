"""Comprehensive feature matrix tests for SlimSchema.

This test file ensures all documented SlimSchema features are tested for:
1. YAML parsing (from_yaml)
2. JSON Schema generation (to_json_schema)
3. Validation (validate)

Each feature from the README is tested to ensure complete coverage.
"""

from __future__ import annotations

import textwrap

import pytest

from slimschema import Schema


def yaml(s: str) -> str:
    """Helper to dedent and strip YAML strings."""
    return textwrap.dedent(s).strip()


@pytest.fixture(autouse=True)
def require_native_backend():
    """Skip tests if native backend is not available."""
    import importlib

    import slimschema.backend as backend

    backend = importlib.reload(backend)

    if not backend._native_available or backend._native_parse_yaml is None:
        pytest.skip("Native backend required")


class TestPrimitiveTypes:
    """Test all primitive types: str, int, float, bool, obj, any."""

    def test_str(self):
        schema = Schema.from_yaml("name: str")
        js = schema.to_json_schema()
        assert js["properties"]["name"]["type"] == "string"
        assert schema.validate({"name": "hello"}).valid

    def test_int(self):
        schema = Schema.from_yaml("count: int")
        js = schema.to_json_schema()
        assert js["properties"]["count"]["type"] == "integer"
        assert schema.validate({"count": 42}).valid
        assert not schema.validate({"count": "42"}).valid

    def test_float(self):
        schema = Schema.from_yaml("score: float")
        js = schema.to_json_schema()
        assert js["properties"]["score"]["type"] == "number"
        assert schema.validate({"score": 3.14}).valid

    def test_bool(self):
        schema = Schema.from_yaml("active: bool")
        js = schema.to_json_schema()
        assert js["properties"]["active"]["type"] == "boolean"
        assert schema.validate({"active": True}).valid
        assert schema.validate({"active": False}).valid

    def test_obj(self):
        schema = Schema.from_yaml("data: obj")
        js = schema.to_json_schema()
        assert js["properties"]["data"]["type"] == "object"
        assert schema.validate({"data": {"key": "value"}}).valid

    def test_any(self):
        schema = Schema.from_yaml("anything: any")
        js = schema.to_json_schema()
        # 'any' should not constrain the type
        assert "type" not in js["properties"]["anything"]
        assert schema.validate({"anything": "string"}).valid
        assert schema.validate({"anything": 123}).valid
        assert schema.validate({"anything": True}).valid
        assert schema.validate({"anything": {"nested": "obj"}}).valid


class TestFormatTypes:
    """Test format types: email, url, date, datetime, uuid."""

    def test_email(self):
        schema = Schema.from_yaml("contact: email")
        js = schema.to_json_schema()
        assert js["properties"]["contact"]["type"] == "string"
        assert js["properties"]["contact"]["format"] == "email"

    def test_url(self):
        schema = Schema.from_yaml("website: url")
        js = schema.to_json_schema()
        assert js["properties"]["website"]["type"] == "string"
        assert js["properties"]["website"]["format"] == "uri"

    def test_date(self):
        schema = Schema.from_yaml("birthday: date")
        js = schema.to_json_schema()
        assert js["properties"]["birthday"]["type"] == "string"
        assert js["properties"]["birthday"]["format"] == "date"

    def test_datetime(self):
        schema = Schema.from_yaml("timestamp: datetime")
        js = schema.to_json_schema()
        assert js["properties"]["timestamp"]["type"] == "string"
        assert js["properties"]["timestamp"]["format"] == "date-time"

    def test_uuid(self):
        schema = Schema.from_yaml("user_id: uuid")
        js = schema.to_json_schema()
        assert js["properties"]["user_id"]["type"] == "string"
        assert js["properties"]["user_id"]["format"] == "uuid"


class TestConstraints:
    """Test constraints: str{min..max}, min..max, /regex/."""

    def test_string_length(self):
        schema = Schema.from_yaml("username: str{3..50}")
        js = schema.to_json_schema()
        prop = js["properties"]["username"]
        assert prop["type"] == "string"
        assert prop["minLength"] == 3
        assert prop["maxLength"] == 50

    def test_string_length_exact(self):
        """Test exact length (min == max)."""
        schema = Schema.from_yaml("code: str{6..6}")
        js = schema.to_json_schema()
        prop = js["properties"]["code"]
        assert prop["minLength"] == 6
        assert prop["maxLength"] == 6

    def test_string_length_zero_min(self):
        """Test zero minimum length."""
        schema = Schema.from_yaml("bio: str{0..500}")
        js = schema.to_json_schema()
        prop = js["properties"]["bio"]
        assert prop["minLength"] == 0
        assert prop["maxLength"] == 500

    def test_string_length_issue_case(self):
        """Test the specific case mentioned in the issue: str{2..50}."""
        schema = Schema.from_yaml("name: str{2..50}")
        js = schema.to_json_schema()
        prop = js["properties"]["name"]
        assert prop["minLength"] == 2
        assert prop["maxLength"] == 50

    def test_integer_range(self):
        schema = Schema.from_yaml("age: 18..120")
        js = schema.to_json_schema()
        prop = js["properties"]["age"]
        assert prop["type"] == "integer"
        assert prop["minimum"] == 18
        assert prop["maximum"] == 120

    def test_integer_range_negative(self):
        schema = Schema.from_yaml("temp: -50..50")
        js = schema.to_json_schema()
        prop = js["properties"]["temp"]
        assert prop["minimum"] == -50
        assert prop["maximum"] == 50

    def test_float_range(self):
        schema = Schema.from_yaml("ratio: 0.0..1.0")
        js = schema.to_json_schema()
        prop = js["properties"]["ratio"]
        assert prop["type"] == "number"
        assert prop["minimum"] == 0.0
        assert prop["maximum"] == 1.0

    def test_float_range_decimal(self):
        schema = Schema.from_yaml("score: 0.5..9.5")
        js = schema.to_json_schema()
        prop = js["properties"]["score"]
        assert prop["minimum"] == 0.5
        assert prop["maximum"] == 9.5

    def test_regex_pattern(self):
        schema = Schema.from_yaml(r"code: /^[A-Z]{3}$/")
        js = schema.to_json_schema()
        prop = js["properties"]["code"]
        assert prop["type"] == "string"
        assert prop["pattern"] == "^[A-Z]{3}$"


class TestCollections:
    """Test collections: list[T], set[T], tuple[T1,T2], dict[K,V], [T]."""

    def test_list(self):
        schema = Schema.from_yaml("tags: list[str]")
        js = schema.to_json_schema()
        prop = js["properties"]["tags"]
        assert prop["type"] == "array"
        assert prop["items"]["type"] == "string"

    def test_list_bare(self):
        """Test bare list without element type."""
        schema = Schema.from_yaml("items: list")
        js = schema.to_json_schema()
        prop = js["properties"]["items"]
        assert prop["type"] == "array"

    def test_set(self):
        schema = Schema.from_yaml("unique_ids: set[int]")
        js = schema.to_json_schema()
        prop = js["properties"]["unique_ids"]
        assert prop["type"] == "array"
        assert prop["uniqueItems"] is True
        assert prop["items"]["type"] == "integer"

    def test_tuple(self):
        schema = Schema.from_yaml("coords: tuple[float, float]")
        js = schema.to_json_schema()
        prop = js["properties"]["coords"]
        assert prop["type"] == "array"
        assert "prefixItems" in prop
        assert len(prop["prefixItems"]) == 2
        assert prop["minItems"] == 2
        assert prop["maxItems"] == 2

    def test_dict(self):
        schema = Schema.from_yaml("scores: dict[str, int]")
        js = schema.to_json_schema()
        prop = js["properties"]["scores"]
        assert prop["type"] == "object"
        assert prop["additionalProperties"]["type"] == "integer"

    def test_dict_bare(self):
        """Test bare dict without types."""
        schema = Schema.from_yaml("config: dict")
        js = schema.to_json_schema()
        prop = js["properties"]["config"]
        assert prop["type"] == "object"

    def test_array_shorthand(self):
        """Test [T] syntax as shorthand for list[T]."""
        schema = Schema.from_yaml("items: [str]")
        js = schema.to_json_schema()
        prop = js["properties"]["items"]
        assert prop["type"] == "array"
        assert prop["items"]["type"] == "string"


class TestEnumsAndUnions:
    """Test enums and unions: a | b | c, str | int."""

    def test_enum(self):
        schema = Schema.from_yaml("status: active | pending | done")
        js = schema.to_json_schema()
        prop = js["properties"]["status"]
        assert prop["type"] == "string"
        assert prop["enum"] == ["active", "pending", "done"]

    def test_union_basic(self):
        schema = Schema.from_yaml("value: str | int")
        js = schema.to_json_schema()
        prop = js["properties"]["value"]
        assert "oneOf" in prop
        types = [item["type"] for item in prop["oneOf"]]
        assert "string" in types
        assert "integer" in types

    def test_union_with_ranges(self):
        """Test union of constrained types."""
        schema = Schema.from_yaml("value: 1..10 | 100..200")
        js = schema.to_json_schema()
        prop = js["properties"]["value"]
        assert "oneOf" in prop


class TestOptionalAndNullable:
    """Test optional (? prefix) and nullable (? suffix)."""

    def test_optional_field(self):
        schema = Schema.from_yaml("?nickname: str")
        js = schema.to_json_schema()
        assert "nickname" in js["properties"]
        assert "nickname" not in js.get("required", [])

    def test_nullable_field(self):
        schema = Schema.from_yaml("rating: float?")
        js = schema.to_json_schema()
        prop = js["properties"]["rating"]
        # Nullable type should be array ["number", "null"]
        assert isinstance(prop["type"], list)
        assert "number" in prop["type"]
        assert "null" in prop["type"]

    def test_optional_and_nullable(self):
        schema = Schema.from_yaml("?notes: str?")
        js = schema.to_json_schema()
        assert "notes" in js["properties"]
        assert "notes" not in js.get("required", [])
        prop = js["properties"]["notes"]
        assert isinstance(prop["type"], list)
        assert "null" in prop["type"]


class TestHiddenFields:
    """Test hidden fields (_ prefix)."""

    def test_hidden_excluded_from_schema(self):
        schema = Schema.from_yaml(yaml("""
            name: str
            _internal: str
            age: int
        """))
        js = schema.to_json_schema()
        props = js["properties"]
        assert "name" in props
        assert "age" in props
        # Hidden field should be excluded
        assert "internal" not in props
        assert "_internal" not in props

    def test_hidden_optional(self):
        schema = Schema.from_yaml("_?secret: str")
        js = schema.to_json_schema()
        # Hidden + optional field should be excluded from JSON Schema
        assert "secret" not in js["properties"]


class TestDefaultValues:
    """Test default values: type = value."""

    def test_default_int(self):
        schema = Schema.from_yaml("count: int = 0")
        js = schema.to_json_schema()
        assert js["properties"]["count"]["default"] == 0

    def test_default_bool(self):
        schema = Schema.from_yaml("active: bool = true")
        js = schema.to_json_schema()
        assert js["properties"]["active"]["default"] is True

    def test_default_string(self):
        schema = Schema.from_yaml('role: str = "user"')
        js = schema.to_json_schema()
        assert js["properties"]["role"]["default"] == "user"

    def test_default_list(self):
        schema = Schema.from_yaml("items: list = []")
        js = schema.to_json_schema()
        assert js["properties"]["items"]["default"] == []

    def test_default_dict(self):
        schema = Schema.from_yaml("config: dict = {}")
        js = schema.to_json_schema()
        assert js["properties"]["config"]["default"] == {}

    def test_field_with_default_not_required(self):
        schema = Schema.from_yaml(yaml("""
            name: str
            count: int = 0
        """))
        js = schema.to_json_schema()
        required = js.get("required", [])
        assert "name" in required
        assert "count" not in required


class TestNestedStructures:
    """Test nested objects and inline objects."""

    def test_nested_object(self):
        schema = Schema.from_yaml(yaml("""
            user:
              name: str
              age: int
        """))
        js = schema.to_json_schema()
        user_prop = js["properties"]["user"]
        assert user_prop["type"] == "object"
        assert "name" in user_prop["properties"]
        assert "age" in user_prop["properties"]

    def test_deeply_nested(self):
        schema = Schema.from_yaml(yaml("""
            company:
              name: str
              address:
                street: str
                city: str
        """))
        js = schema.to_json_schema()
        company = js["properties"]["company"]
        address = company["properties"]["address"]
        assert address["type"] == "object"
        assert "street" in address["properties"]

    def test_inline_object(self):
        schema = Schema.from_yaml("point: {x: float, y: float}")
        js = schema.to_json_schema()
        point = js["properties"]["point"]
        assert point["type"] == "object"
        assert "x" in point["properties"]
        assert "y" in point["properties"]


class TestYamlListSyntax:
    """Test YAML list syntax with - prefix."""

    def test_basic_list_items(self):
        schema = Schema.from_yaml(yaml("""
            issues:
              - file: str
                line: int
                message: str
        """))
        js = schema.to_json_schema()
        issues = js["properties"]["issues"]
        assert issues["type"] == "array"
        items = issues["items"]
        assert items["type"] == "object"
        assert "file" in items["properties"]
        assert "line" in items["properties"]

    def test_list_in_nested_object(self):
        schema = Schema.from_yaml(yaml("""
            response:
              success: bool
              items:
                - id: int
                  name: str
        """))
        js = schema.to_json_schema()
        response = js["properties"]["response"]
        items_prop = response["properties"]["items"]
        assert items_prop["type"] == "array"

    def test_botassembly_pattern(self):
        """Test the exact BotAssembly agent response pattern."""
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
        js = schema.to_json_schema()
        props = js["properties"]

        assert props["summary"]["type"] == "object"
        assert props["issues"]["type"] == "array"
        assert props["success"]["type"] == "boolean"


class TestValidation:
    """Test validation with all feature types."""

    def test_validate_string_length(self):
        schema = Schema.from_yaml("name: str{2..50}")
        assert schema.validate({"name": "Alice"}).valid
        assert schema.validate({"name": "A"}).valid is False  # Too short
        assert schema.validate({"name": "A" * 100}).valid is False  # Too long

    def test_validate_integer_range(self):
        schema = Schema.from_yaml("age: 18..120")
        assert schema.validate({"age": 25}).valid
        assert schema.validate({"age": 10}).valid is False  # Too low
        assert schema.validate({"age": 200}).valid is False  # Too high

    def test_validate_list_items(self):
        schema = Schema.from_yaml(yaml("""
            items:
              - id: int
                name: str
        """))
        assert schema.validate({
            "items": [
                {"id": 1, "name": "A"},
                {"id": 2, "name": "B"},
            ]
        }).valid

        # Invalid item
        result = schema.validate({
            "items": [
                {"id": "not-int", "name": "A"},
            ]
        })
        assert result.valid is False


class TestComplexSchemas:
    """Test complex real-world schema patterns."""

    def test_api_response_schema(self):
        """Test a typical API response schema with all features."""
        schema = Schema.from_yaml(yaml("""
            success: bool
            ?error: str
            data:
              total: int
              page: 1..100
              items:
                - id: uuid
                  name: str{1..100}
                  ?tags: list[str]
                  status: active | pending | done
                  created: datetime
        """))
        js = schema.to_json_schema()

        # Verify structure
        assert js["properties"]["success"]["type"] == "boolean"
        assert "error" not in js.get("required", [])

        data = js["properties"]["data"]
        assert data["properties"]["page"]["minimum"] == 1
        assert data["properties"]["page"]["maximum"] == 100

        items = data["properties"]["items"]
        assert items["type"] == "array"
        item_props = items["items"]["properties"]
        assert item_props["id"]["format"] == "uuid"
        assert item_props["name"]["minLength"] == 1
        assert item_props["status"]["enum"] == ["active", "pending", "done"]
