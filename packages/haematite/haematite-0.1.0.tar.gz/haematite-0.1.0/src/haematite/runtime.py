"""Haematite runtime implementation for Python.

Handles variable extraction, explicit exports, and snapshots.
Communicates with the Haematite executor via a temp file specified
in the HAEMATITE_EXPORT_FILE environment variable.
"""

import atexit
import inspect
import json
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set


# Global state for exports
_exports: Dict[str, Dict[str, Any]] = {}
_snapshots: Dict[str, Dict[str, Any]] = {}
_errors: List[Dict[str, str]] = []
_requested_extractions: List[str] = []
_atexit_registered: bool = False


def _get_type_name(value: Any) -> str:
    """Determine the JSON type name for a value."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, (list, tuple)):
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return "string"  # Fall back to string representation


def _serialize_value(value: Any, seen: Optional[Set[int]] = None) -> Any:
    """Serialize a value to JSON-compatible format with circular reference detection."""
    if seen is None:
        seen = set()

    # Check for circular reference
    if isinstance(value, (dict, list)) and id(value) in seen:
        raise ValueError("Circular reference detected")

    if value is None:
        return None
    elif isinstance(value, bool):
        return value
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        return value
    elif isinstance(value, (list, tuple)):
        seen.add(id(value))
        result = [_serialize_value(item, seen) for item in value]
        seen.discard(id(value))
        return result
    elif isinstance(value, dict):
        seen.add(id(value))
        result = {str(k): _serialize_value(v, seen) for k, v in value.items()}
        seen.discard(id(value))
        return result
    elif hasattr(value, "__dict__"):
        # Object with attributes - try to serialize as dict
        seen.add(id(value))
        try:
            result = {k: _serialize_value(v, seen) for k, v in value.__dict__.items()
                      if not k.startswith("_")}
            seen.discard(id(value))
            return result
        except Exception:
            seen.discard(id(value))
            return f"<{type(value).__name__}>"
    elif callable(value):
        return f"<function:{getattr(value, '__name__', 'anonymous')}>"
    else:
        # Fall back to string representation
        return str(value)


def _create_exported_value(value: Any) -> Dict[str, Any]:
    """Create an ExportedValue structure."""
    try:
        serialized = _serialize_value(value)
        return {
            "type": _get_type_name(value),
            "value": serialized
        }
    except ValueError as e:
        # Circular reference or other serialization error
        raise e


def export(name: str, value: Any) -> None:
    """Explicitly export a value with the given name.

    This captures the value at the point of the call, not at the end
    of execution. Later calls with the same name will overwrite.

    Args:
        name: The name to export the value under
        value: The value to export (must be JSON-serializable)

    Example:
        import haematite as hm

        data = [1, 2, 3]
        hm.export("before", data.copy())
        data.append(4)
        hm.export("after", data)
    """
    global _exports, _errors, _atexit_registered

    # Ensure atexit handler is registered
    if not _atexit_registered:
        atexit.register(_write_export_file)
        _atexit_registered = True

    try:
        _exports[name] = _create_exported_value(value)
    except ValueError as e:
        _errors.append({
            "variable": name,
            "error": str(e)
        })


def snapshot(label: str, filter_vars: Optional[List[str]] = None) -> None:
    """Capture a point-in-time snapshot of local variables.

    Captures all local variables from the caller's frame, or a filtered
    subset if filter_vars is provided.

    Args:
        label: A name for this snapshot
        filter_vars: Optional list of variable names to include.
                    If None, all local variables are captured.

    Example:
        import haematite as hm

        x = 1
        y = 2
        hm.snapshot("step1")

        x = 10
        hm.snapshot("step2")
    """
    global _snapshots, _errors, _atexit_registered

    # Ensure atexit handler is registered
    if not _atexit_registered:
        atexit.register(_write_export_file)
        _atexit_registered = True

    # Get caller's local variables
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        _errors.append({
            "variable": f"snapshot:{label}",
            "error": "Could not access caller frame"
        })
        return

    try:
        caller_locals = frame.f_back.f_locals.copy()
    finally:
        del frame

    # Filter variables
    if filter_vars is not None:
        caller_locals = {k: v for k, v in caller_locals.items() if k in filter_vars}

    # Exclude internal haematite variables and modules
    excluded = {"hm", "__builtins__", "__name__", "__doc__", "__package__",
                "__loader__", "__spec__", "__annotations__", "__cached__"}
    caller_locals = {k: v for k, v in caller_locals.items()
                     if k not in excluded and not k.startswith("_")}

    # Serialize all variables
    variables = {}
    for name, value in caller_locals.items():
        try:
            variables[name] = _create_exported_value(value)
        except ValueError as e:
            _errors.append({
                "variable": f"{label}.{name}",
                "error": str(e)
            })

    _snapshots[label] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "variables": variables
    }


def _request_extraction(var_names: List[str]) -> None:
    """Register variables for automatic extraction at end of execution.

    This is called by the Haematite executor based on the exports DMZ.
    Users typically don't call this directly.

    Args:
        var_names: List of variable names to extract from the global scope
    """
    global _requested_extractions, _atexit_registered

    _requested_extractions.extend(var_names)

    # Register atexit handler if not already done
    if not _atexit_registered:
        atexit.register(_write_export_file)
        _atexit_registered = True


def _complete_extraction(values: Dict[str, Any]) -> None:
    """Complete extraction by receiving the actual variable values.

    This is called by injected cleanup code at the end of the script,
    passing the actual values of requested variables.

    Args:
        values: Dict mapping variable names to their values
    """
    global _exports, _errors, _requested_extractions

    for var_name in _requested_extractions:
        # Skip if already explicitly exported
        if var_name in _exports:
            continue

        if var_name in values and values[var_name] is not None:
            try:
                _exports[var_name] = _create_exported_value(values[var_name])
            except ValueError as e:
                _errors.append({
                    "variable": var_name,
                    "error": str(e)
                })
        else:
            _errors.append({
                "variable": var_name,
                "error": f"Variable '{var_name}' not found in scope"
            })


def _extract_requested_variables() -> None:
    """Extract variables requested via _request_extraction from caller's globals."""
    global _exports, _errors, _requested_extractions

    if not _requested_extractions:
        return

    # Walk up the call stack to find the main script's globals
    frame = inspect.currentframe()
    main_globals = {}

    try:
        current = frame
        while current is not None:
            # Look for the __main__ module or the outermost frame
            if current.f_globals.get("__name__") == "__main__":
                main_globals = current.f_globals
                break
            # Also check locals for variables
            main_globals.update(current.f_locals)
            current = current.f_back
    finally:
        del frame

    for var_name in _requested_extractions:
        # Skip if already explicitly exported
        if var_name in _exports:
            continue

        if var_name in main_globals:
            try:
                _exports[var_name] = _create_exported_value(main_globals[var_name])
            except ValueError as e:
                _errors.append({
                    "variable": var_name,
                    "error": str(e)
                })
        else:
            _errors.append({
                "variable": var_name,
                "error": f"Variable '{var_name}' not found in scope"
            })


def _write_export_file() -> None:
    """Write all exports, snapshots, and errors to the export file."""
    global _exports, _snapshots, _errors

    export_path = os.environ.get("HAEMATITE_EXPORT_FILE")
    if not export_path:
        return

    # Extract any requested variables before writing
    _extract_requested_variables()

    # Build the export file structure
    export_data: Dict[str, Any] = {
        "exports": _exports
    }

    if _snapshots:
        export_data["snapshots"] = _snapshots

    if _errors:
        export_data["errors"] = _errors

    try:
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)
    except Exception:
        # Silent failure - executor will handle missing file
        pass
