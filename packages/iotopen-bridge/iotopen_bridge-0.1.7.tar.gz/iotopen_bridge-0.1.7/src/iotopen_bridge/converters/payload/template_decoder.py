# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/payload/template_decoder.py
from __future__ import annotations

import json
import string
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, cast

from ...core.errors import ValidationError
from ...security.validation.json_safety import validate_json_value
from ...security.validation.limits import Limits, enforce_payload
from .base import DecodeError, DecoderContext


def _maybe_json(b: bytes, *, limits: Limits) -> Any:
    try:
        s = b.decode("utf-8", "ignore").strip()
        if not s:
            return None
        if not (s.startswith("{") or s.startswith("[")):
            return None
        obj = json.loads(s)
        validate_json_value(obj, limits=limits)
        return obj
    except Exception:
        return None


def _get_dotted_path(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        part = part.strip()
        if part == "":
            continue
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except Exception:
                return None
        else:
            return None
    return cur


def _get_json_pointer(obj: Any, ptr: str) -> Any:
    # Minimal RFC6901-style pointer: "/a/0/b"
    p = (ptr or "").strip()
    if p == "" or p == "/":
        return obj
    if not p.startswith("/"):
        return None

    cur = obj
    for raw in p.split("/")[1:]:
        seg = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict):
            cur = cur.get(seg)
        elif isinstance(cur, list):
            try:
                cur = cur[int(seg)]
            except Exception:
                return None
        else:
            return None
    return cur


class _SafeFormatter(string.Formatter):
    __slots__ = ()

    def get_field(
        self, field_name: str, args: Sequence[Any], kwargs: Mapping[str, Any]
    ) -> tuple[Any, str]:
        # Only allow {value} and {topic}
        if field_name not in ("value", "topic"):
            raise ValueError(f"unsupported placeholder: {field_name}")

        # typeshed/mypy often types string.Formatter.get_field as Any at runtime.
        obj, used_key = cast(tuple[Any, Any], super().get_field(field_name, args, kwargs))
        return obj, str(used_key)


_FMT = _SafeFormatter()


@dataclass(frozen=True)
class TemplateDecoder:
    """Extract/format values from payload safely (no eval).

    Supported extraction:
      - dotted json_path="a.b.0.c"
      - json_pointer="/a/b/0/c"
    Supported formatting:
      - "{value}" and "{topic}" only (safe formatter)
    """

    json_path: str | None = None
    json_pointer: str | None = None
    format: str | None = None
    default: Any = None
    limits: Limits = field(default_factory=Limits)

    def decode(
        self,
        payload: bytes | bytearray | memoryview | str,
        *,
        topic: str | None = None,
        ctx: DecoderContext | None = None,
    ) -> Any:
        try:
            b = enforce_payload(payload, self.limits)
        except ValidationError as e:
            raise DecodeError(str(e)) from e

        obj = _maybe_json(b, limits=self.limits)
        value: Any = None

        if self.json_path or self.json_pointer:
            if obj is None:
                if self.default is not None:
                    value = self.default
                else:
                    raise DecodeError("json_path/json_pointer requires JSON payload")

            if self.json_pointer:
                value = _get_json_pointer(obj, self.json_pointer)
            else:
                value = _get_dotted_path(obj, self.json_path or "")

            if value is None and self.default is not None:
                value = self.default
        else:
            value = b.decode("utf-8", "ignore").strip()

        if self.format:
            try:
                return _FMT.format(str(self.format), value=value, topic=topic or "")
            except Exception as e:
                raise DecodeError(f"format failed: {e}") from e

        return value
