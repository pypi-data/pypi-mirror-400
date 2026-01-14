"""Shared library resource for RiyadhAI RTC.

This is not a Python extension module. It exists to avoid accidental imports of the
`libriyadhai_ffi.so` shared library as if it were a CPython extension.
"""

from __future__ import annotations

import atexit
from contextlib import ExitStack
from importlib.resources import as_file, files

_resource_files = ExitStack()
atexit.register(_resource_files.close)


def get_path() -> str:
    """Return a filesystem path to the bundled shared library."""
    res = files("riyadhai.rtc.resources") / "bin" / "libriyadhai_ffi.so"
    ctx = as_file(res)
    path = _resource_files.enter_context(ctx)
    return str(path)
