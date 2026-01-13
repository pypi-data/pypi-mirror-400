# File: src/iotopen_bridge/converters/normalize/enum.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any


def to_enum_key(value: Any) -> str | None:
    """Normalize values into stable enum-like keys (lower_snake)."""
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8", "ignore")
        except Exception:
            return None
    s = str(value).strip()
    if not s:
        return None
    s = s.replace("-", "_").replace(" ", "_").lower()
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_") or None
