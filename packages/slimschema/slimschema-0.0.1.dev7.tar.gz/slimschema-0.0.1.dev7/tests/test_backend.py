"""Tests for validation backend selection and fallback behavior."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType

import pytest


def _reload_backend(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    import slimschema.backend as backend

    return importlib.reload(backend)


def test_validate_json_falls_back_to_jsonschema(monkeypatch: pytest.MonkeyPatch):
    import slimschema.backend as backend

    monkeypatch.setattr(backend, "_native_available", False)
    monkeypatch.setattr(backend, "_native_validate", None)

    schema = {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {"type": "integer"}},
        },
        "required": ["items"],
        "additionalProperties": False,
    }

    assert backend.validate_json(schema, {"items": [1, 2]}) == {"valid": True}

    result = backend.validate_json(schema, {"items": ["x"]})
    assert result["valid"] is False
    assert result["errors"][0]["path"] == "$.items[0]"


def test_validate_json_uses_native_module_from_sys_path(monkeypatch: pytest.MonkeyPatch):
    fake = ModuleType("slimschema_native")

    def fake_validate_json(schema, data):
        return {"valid": True, "backend": "fake"}

    fake.validate_json = fake_validate_json  # type: ignore[attr-defined]
    fake.get_version = lambda: "test-version"  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "slimschema_native", fake)

    backend = _reload_backend(monkeypatch)
    assert backend.is_native_available() is True
    assert backend.validate_json({"type": "object"}, {})["backend"] == "fake"
    assert backend.get_backend_info()["native_version"] == "test-version"

    monkeypatch.delitem(sys.modules, "slimschema_native", raising=False)
    _reload_backend(monkeypatch)


def test_native_version_failure_is_ignored(monkeypatch: pytest.MonkeyPatch):
    fake = ModuleType("slimschema_native")

    def fake_validate_json(schema, data):
        return {"valid": True, "backend": "fake"}

    def bad_version():
        raise RuntimeError("boom")

    fake.validate_json = fake_validate_json  # type: ignore[attr-defined]
    fake.get_version = bad_version  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "slimschema_native", fake)

    backend = _reload_backend(monkeypatch)
    assert backend.is_native_available() is True
    assert backend.get_backend_info()["native_version"] is None

    monkeypatch.delitem(sys.modules, "slimschema_native", raising=False)
    _reload_backend(monkeypatch)


def test_validate_json_cached_delegates(monkeypatch: pytest.MonkeyPatch):
    import slimschema.backend as backend

    monkeypatch.setattr(backend, "validate_json", lambda s, d: {"valid": True, "x": 1})
    assert backend.validate_json_cached({"type": "object"}, {}) == {"valid": True, "x": 1}


def test_backend_import_fallbacks_handle_missing_native(monkeypatch: pytest.MonkeyPatch):
    import builtins
    import sys

    import slimschema

    # Save original state to restore later
    saved_modules = {}
    module_names = (
        "slimschema_native",
        "slimschema.slimschema_native",
        "slimschema._native.slimschema_native",
    )
    for name in module_names:
        if name in sys.modules:
            saved_modules[name] = sys.modules.pop(name)

    saved_attr = None
    if hasattr(slimschema, "slimschema_native"):
        saved_attr = getattr(slimschema, "slimschema_native")
        delattr(slimschema, "slimschema_native")

    native_pkg = sys.modules.get("slimschema._native")
    saved_native_pkg_attr = None
    if native_pkg is not None and hasattr(native_pkg, "slimschema_native"):
        saved_native_pkg_attr = getattr(native_pkg, "slimschema_native")
        delattr(native_pkg, "slimschema_native")

    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "slimschema_native":
            raise ImportError("blocked")
        if fromlist and "slimschema_native" in fromlist:
            raise ImportError("blocked")
        return orig_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    backend = _reload_backend(monkeypatch)
    assert backend.is_native_available() is False

    # Restore state for subsequent tests
    monkeypatch.undo()

    # Restore sys.modules
    for name, mod in saved_modules.items():
        sys.modules[name] = mod

    # Restore attributes
    if saved_attr is not None:
        setattr(slimschema, "slimschema_native", saved_attr)
    if saved_native_pkg_attr is not None and native_pkg is not None:
        setattr(native_pkg, "slimschema_native", saved_native_pkg_attr)

    # Reload backend to pick up restored modules
    _reload_backend(monkeypatch)


def test_result_to_dict_with_heap_type(monkeypatch: pytest.MonkeyPatch):
    """Test _result_to_dict converts heap type ValidationResult to dict."""
    import slimschema.backend as backend

    class FakeError:
        def __init__(self, path: str, message: str):
            self.path = path
            self.message = message

    class FakeResult:
        def __init__(self, valid: bool, errors: list):
            self.valid = valid
            self.errors = errors

    # Test valid result
    result = backend._result_to_dict(FakeResult(True, []))
    assert result == {"valid": True}

    # Test invalid result with errors
    result = backend._result_to_dict(
        FakeResult(False, [FakeError("$.name", "type mismatch")])
    )
    assert result == {"valid": False, "errors": [{"path": "$.name", "message": "type mismatch"}]}

    # Test dict passthrough
    result = backend._result_to_dict({"valid": True, "extra": "field"})
    assert result == {"valid": True, "extra": "field"}


def test_result_to_dict_fallback_on_error(monkeypatch: pytest.MonkeyPatch):
    """Test _result_to_dict handles unexpected object types gracefully."""
    import slimschema.backend as backend

    # Test object that raises TypeError when checking valid
    class BadResult:
        @property
        def valid(self):
            raise TypeError("broken")

        @property
        def errors(self):
            return []

    result = backend._result_to_dict(BadResult())
    # Falls back to bool() which catches the error
    # bool(BadResult()) returns True since no __bool__ is defined
    assert result == {"valid": True, "errors": []}


def test_validate_json_bytes_native(monkeypatch: pytest.MonkeyPatch):
    """Test validate_json_bytes uses native backend when available."""
    import slimschema.backend as backend

    class FakeResult:
        def __init__(self, valid: bool):
            self.valid = valid
            self.errors = []

    def fake_validate_bytes(schema, data):
        return FakeResult(True)

    monkeypatch.setattr(backend, "_native_available", True)
    monkeypatch.setattr(backend, "_native_validate_bytes", fake_validate_bytes)

    result = backend.validate_json_bytes({"type": "object"}, b'{"name": "test"}')
    assert result == {"valid": True}


def test_validate_json_bytes_fallback(monkeypatch: pytest.MonkeyPatch):
    """Test validate_json_bytes falls back to validate_json when native unavailable."""
    import slimschema.backend as backend

    monkeypatch.setattr(backend, "_native_available", False)
    monkeypatch.setattr(backend, "_native_validate_bytes", None)

    schema = {"type": "object", "properties": {"name": {"type": "string"}}}

    # Test with bytes
    result = backend.validate_json_bytes(schema, b'{"name": "Alice"}')
    assert result["valid"] is True

    # Test with str
    result = backend.validate_json_bytes(schema, '{"name": "Bob"}')
    assert result["valid"] is True

    # Test with bytearray
    result = backend.validate_json_bytes(schema, bytearray(b'{"name": "Charlie"}'))
    assert result["valid"] is True

    # Test with memoryview (special handling in fallback)
    result = backend.validate_json_bytes(schema, memoryview(b'{"name": "David"}'))
    assert result["valid"] is True


def test_get_backend_info_with_heap_types(monkeypatch: pytest.MonkeyPatch):
    """Test get_backend_info reports heap type and buffer protocol support."""
    import slimschema.backend as backend

    monkeypatch.setattr(backend, "_native_available", True)
    monkeypatch.setattr(backend, "_native_version", "0.3.0")
    monkeypatch.setattr(backend, "_ValidationResult", object)
    monkeypatch.setattr(backend, "_native_validate_bytes", lambda s, d: None)

    info = backend.get_backend_info()
    assert info["has_heap_types"] is True
    assert info["has_buffer_protocol"] is True

    monkeypatch.setattr(backend, "_ValidationResult", None)
    monkeypatch.setattr(backend, "_native_validate_bytes", None)

    info = backend.get_backend_info()
    assert info["has_heap_types"] is False
    assert info["has_buffer_protocol"] is False
