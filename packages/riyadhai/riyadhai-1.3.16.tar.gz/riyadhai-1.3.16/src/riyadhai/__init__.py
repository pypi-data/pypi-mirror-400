# Copyright 2026 RiyadhAI LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""RiyadhAI SDK.

This package provides:
- `riyadhai.agents`: realtime agent framework.
- `riyadhai.api`: server API client (Twirp).
- `riyadhai.protocol`: protocol buffer definitions used by the API.
- `riyadhai.rtc`: realtime communication helpers.
"""

from __future__ import annotations

import importlib
import typing
from types import ModuleType as _ModuleType

__all__ = ["agents", "api", "protocol", "rtc"]

if typing.TYPE_CHECKING:
    from . import agents as agents
    from . import api as api
    from . import protocol as protocol
    from . import rtc as rtc
else:
    agents: _ModuleType
    api: _ModuleType
    protocol: _ModuleType
    rtc: _ModuleType


def __getattr__(name: str) -> typing.Any:
    if name in __all__:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
