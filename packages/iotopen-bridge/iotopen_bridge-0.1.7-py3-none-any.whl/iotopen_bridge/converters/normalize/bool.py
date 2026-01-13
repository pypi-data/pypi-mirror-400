# File: src/iotopen_bridge/converters/normalize/bool.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any

_TRUE = {"1", "true", "t", "yes", "y", "on", "enabled", "enable"}
_FALSE = {"0", "false", "f", "no", "n", "off", "disabled", "disable"}


def to_bool(value: Any) -> bool | None:
    """Best-effort bool normalization.

    Returns:
      - True/False when confidently parsed
      - None when ambiguous
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False
        return None
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8", "ignore")
        except Exception:
            return None
    if isinstance(value, str):
        s = value.strip().lower()
        if s in _TRUE:
            return True
        if s in _FALSE:
            return False
    return None


def to_bool_strict(value: Any) -> bool:
    """Strict bool normalization (raises on ambiguity)."""
    b = to_bool(value)
    if b is None:
        raise ValueError(f"Cannot interpret as bool: {value!r}")
    return b
