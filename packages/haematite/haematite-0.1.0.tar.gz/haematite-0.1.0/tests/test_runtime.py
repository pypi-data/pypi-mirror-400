"""Tests for haematite runtime."""

import json
import os
import tempfile
from unittest import mock

import pytest

from haematite import export, snapshot, _request_extraction
from haematite.runtime import (
    _exports,
    _snapshots,
    _errors,
    _requested_extractions,
    _get_type_name,
    _serialize_value,
    _create_exported_value,
    _write_export_file,
)


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global state before each test."""
    import haematite.runtime as rt
    rt._exports.clear()
    rt._snapshots.clear()
    rt._errors.clear()
    rt._requested_extractions.clear()
    rt._atexit_registered = False
    yield


class TestGetTypeName:
    def test_null(self):
        assert _get_type_name(None) == "null"

    def test_boolean(self):
        assert _get_type_name(True) == "boolean"
        assert _get_type_name(False) == "boolean"

    def test_number(self):
        assert _get_type_name(42) == "number"
        assert _get_type_name(3.14) == "number"

    def test_string(self):
        assert _get_type_name("hello") == "string"

    def test_array(self):
        assert _get_type_name([1, 2, 3]) == "array"
        assert _get_type_name((1, 2, 3)) == "array"

    def test_object(self):
        assert _get_type_name({"key": "value"}) == "object"


class TestSerializeValue:
    def test_primitives(self):
        assert _serialize_value(None) is None
        assert _serialize_value(True) is True
        assert _serialize_value(42) == 42
        assert _serialize_value(3.14) == 3.14
        assert _serialize_value("hello") == "hello"

    def test_list(self):
        assert _serialize_value([1, 2, 3]) == [1, 2, 3]

    def test_tuple(self):
        assert _serialize_value((1, 2, 3)) == [1, 2, 3]

    def test_dict(self):
        assert _serialize_value({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    def test_nested(self):
        value = {"items": [1, 2, {"nested": True}]}
        result = _serialize_value(value)
        assert result == {"items": [1, 2, {"nested": True}]}

    def test_circular_reference(self):
        a = []
        a.append(a)
        with pytest.raises(ValueError, match="Circular reference"):
            _serialize_value(a)

    def test_function(self):
        def my_func():
            pass
        result = _serialize_value(my_func)
        assert result == "<function:my_func>"


class TestExport:
    def test_simple_export(self):
        export("result", 42)
        assert "result" in _exports
        assert _exports["result"]["type"] == "number"
        assert _exports["result"]["value"] == 42

    def test_object_export(self):
        export("data", {"name": "Alice", "age": 30})
        assert _exports["data"]["type"] == "object"
        assert _exports["data"]["value"] == {"name": "Alice", "age": 30}

    def test_overwrite_export(self):
        export("x", 1)
        export("x", 2)
        assert _exports["x"]["value"] == 2

    def test_circular_reference_error(self):
        a = []
        a.append(a)
        export("circular", a)
        assert "circular" not in _exports
        assert len(_errors) == 1
        assert _errors[0]["variable"] == "circular"


class TestSnapshot:
    def test_snapshot_captures_locals(self):
        x = 10
        y = "hello"
        snapshot("test")

        assert "test" in _snapshots
        assert "x" in _snapshots["test"]["variables"]
        assert "y" in _snapshots["test"]["variables"]
        assert _snapshots["test"]["variables"]["x"]["value"] == 10
        assert _snapshots["test"]["variables"]["y"]["value"] == "hello"

    def test_snapshot_with_filter(self):
        a = 1
        b = 2
        c = 3
        snapshot("filtered", ["a", "c"])

        assert "a" in _snapshots["filtered"]["variables"]
        assert "c" in _snapshots["filtered"]["variables"]
        assert "b" not in _snapshots["filtered"]["variables"]

    def test_snapshot_has_timestamp(self):
        snapshot("timed")
        assert "timestamp" in _snapshots["timed"]


class TestRequestExtraction:
    def test_registers_variables(self):
        _request_extraction(["a", "b", "c"])
        assert _requested_extractions == ["a", "b", "c"]

    def test_appends_to_existing(self):
        _request_extraction(["a"])
        _request_extraction(["b", "c"])
        assert _requested_extractions == ["a", "b", "c"]


class TestWriteExportFile:
    def test_writes_json(self):
        export("result", 42)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            with mock.patch.dict(os.environ, {"HAEMATITE_EXPORT_FILE": temp_path}):
                _write_export_file()

            with open(temp_path) as f:
                data = json.load(f)

            assert "exports" in data
            assert data["exports"]["result"]["value"] == 42
        finally:
            os.unlink(temp_path)

    def test_no_file_without_env_var(self):
        export("result", 42)
        with mock.patch.dict(os.environ, {}, clear=True):
            if "HAEMATITE_EXPORT_FILE" in os.environ:
                del os.environ["HAEMATITE_EXPORT_FILE"]
            _write_export_file()  # Should not raise
