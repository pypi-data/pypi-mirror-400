# File: src/iotopen_bridge/converters/normalize/number.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any


def to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return None
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8", "ignore")
        except Exception:
            return None
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return int(s, 10)
        except Exception:
            return None
    return None


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8", "ignore")
        except Exception:
            return None
    if isinstance(value, str):
        s = value.strip().replace(",", ".")
        if not s:
            return None
        try:
            return float(s)
        except Exception:
            return None
    return None
