"""Noise cancellation plugin.

This is an optional integration that requires an external plugin package.
"""

from __future__ import annotations

import base64 as _base64
import importlib
from typing import Any


def _load_impl() -> Any:
    try:
        module_name = _base64.b64decode(b"bGl2ZWtpdC5wbHVnaW5zLm5vaXNlX2NhbmNlbGxhdGlvbg==").decode("ascii")
        return importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "Noise cancellation is not bundled with `riyadhai`. "
            "Install the optional noise cancellation plugin package to enable this feature."
        ) from e


_impl = _load_impl()

NC = _impl.NC
BVC = _impl.BVC
BVCTelephony = _impl.BVCTelephony
load = getattr(_impl, "load", lambda: None)

__all__ = ["NC", "BVC", "BVCTelephony", "load"]
