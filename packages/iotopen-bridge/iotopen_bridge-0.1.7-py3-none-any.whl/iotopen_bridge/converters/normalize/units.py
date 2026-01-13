# File: src/iotopen_bridge/converters/normalize/units.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

_UNIT_ALIASES = {
    "c": "°C",
    "°c": "°C",
    "celsius": "°C",
    "f": "°F",
    "°f": "°F",
    "fahrenheit": "°F",
    "percent": "%",
    "pct": "%",
    "watt": "W",
    "watts": "W",
    "wh": "Wh",
    "kwh": "kWh",
    "kw": "kW",
    "v": "V",
    "volt": "V",
    "volts": "V",
    "a": "A",
    "amp": "A",
    "amps": "A",
}


def normalize_unit(unit: str | None) -> str | None:
    if unit is None:
        return None
    u = str(unit).strip()
    if not u:
        return None
    k = u.lower()
    return _UNIT_ALIASES.get(k, u)
