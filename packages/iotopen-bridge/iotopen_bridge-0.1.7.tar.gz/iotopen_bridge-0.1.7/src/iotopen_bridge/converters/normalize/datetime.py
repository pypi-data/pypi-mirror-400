# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/normalize/datetime.py
from __future__ import annotations

import datetime as _dt
from typing import Any


def to_unix_ts(value: Any) -> float | None:
    """Convert common timestamp forms to unix seconds."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        # heuristics: ms vs s
        v = float(value)
        if v > 2_000_000_000_000:  # ~2001 in ms
            return v / 1000.0
        return v

    if isinstance(value, _dt.datetime):
        dt: _dt.datetime = value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_dt.timezone.utc)
        # mypy sometimes loses precision when working with Any; force float
        return float(dt.timestamp())

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
            dt = _dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=_dt.timezone.utc)
            return float(dt.timestamp())
        except Exception:
            return None

    return None


def to_datetime_iso(value: Any) -> str | None:
    """Return ISO 8601 string in UTC (best-effort)."""
    ts = to_unix_ts(value)
    if ts is None:
        return None
    dt = _dt.datetime.fromtimestamp(ts, tz=_dt.timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")
