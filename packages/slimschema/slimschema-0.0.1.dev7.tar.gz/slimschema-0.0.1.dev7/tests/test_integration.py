"""Integration tests for SlimSchema with Zig backend."""

from __future__ import annotations

from typing import Annotated

import pytest

from slimschema import Len, Range, ValidationError, spec


class TestSlimSchemaIntegration:
    """Test SlimSchema Python API with Zig backend."""

    def test_full_validation_flow(self):
        """Test complete validation flow."""

        @spec
        class User:
            name: Annotated[str, Len(1, 50)]
            age: Annotated[int, Range(0, 120)]

        user = User.loads('{"name": "Alice", "age": 30}')
        assert user.name == "Alice"
        assert user.age == 30

    def test_validation_error(self):
        """Test that validation errors propagate correctly."""

        @spec
        class User:
            name: Annotated[str, Len(1, 50)]

        with pytest.raises(ValidationError) as exc:
            User.loads('{"name": ""}')

        # Should have error about minLength
        assert len(exc.value.errors) > 0
