"""Haematite runtime support for Python.

This package provides variable extraction and export functionality
for Haematite notebooks. It is automatically injected into Python
code blocks and communicates with the Haematite executor.

Usage:
    import haematite as hm

    # Explicit export
    hm.export("result", my_value)

    # Point-in-time snapshot
    hm.snapshot("after_transform")
"""

from .runtime import export, snapshot, _request_extraction, _complete_extraction

__all__ = ["export", "snapshot", "_request_extraction", "_complete_extraction"]
__version__ = "0.1.0"
