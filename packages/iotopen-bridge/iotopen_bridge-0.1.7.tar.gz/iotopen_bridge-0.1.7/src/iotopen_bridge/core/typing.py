# File: src/iotopen_bridge/core/typing.py
# SPDX-License-Identifier: Apache-2.0

"""Shared typing helpers (dependency-free)."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Any, Protocol, TypeAlias


class SupportsClose(Protocol):
    def close(self) -> None: ...


StrPath: TypeAlias = str | Path

JSONScalar: TypeAlias = str | int | float | bool | None
JSONObject: TypeAlias = MutableMapping[str, "JSONValue"]
JSONMapping: TypeAlias = Mapping[str, "JSONValue"]
JSONArray: TypeAlias = list["JSONValue"]
JSONSequence: TypeAlias = Sequence["JSONValue"]
JSONValue: TypeAlias = JSONScalar | JSONObject | JSONArray

Headers: TypeAlias = Mapping[str, str]
AnyMapping: TypeAlias = Mapping[str, Any]
