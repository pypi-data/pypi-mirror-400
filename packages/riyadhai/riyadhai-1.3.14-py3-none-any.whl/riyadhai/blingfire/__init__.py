# Copyright 2025 LiveKit, Inc.
# Modifications Copyright 2026 RiyadhAI LLC
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


from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, cast

try:
    import lk_blingfire as _cext  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    _cext = None

from .version import __version__

_MissingImpl = Callable[..., Any]


def is_available() -> bool:
    return _cext is not None


def _require() -> Any:
    if _cext is None:
        raise ModuleNotFoundError(
            "Optional dependency missing: `lk_blingfire`. "
            "This is a native extension used for fast sentence/word splitting. "
            "Install a compatible `lk_blingfire` wheel, or use a tokenizer that doesn't rely on it."
        )
    return _cext


def text_to_sentences(text: str) -> str:
    return _require().text_to_sentences(text)


def text_to_sentences_with_offsets(
    text: str,
) -> tuple[str, list[tuple[int, int]]]:
    return _require().text_to_sentences_with_offsets(text)


def text_to_words(text: str) -> str:
    return _require().text_to_words(text)


def text_to_words_with_offsets(
    text: str,
) -> tuple[str, list[tuple[int, int]]]:
    return _require().text_to_words_with_offsets(text)


__all__ = [
    "is_available",
    "text_to_sentences",
    "text_to_sentences_with_offsets",
    "text_to_words",
    "text_to_words_with_offsets",
    "__version__",
]
