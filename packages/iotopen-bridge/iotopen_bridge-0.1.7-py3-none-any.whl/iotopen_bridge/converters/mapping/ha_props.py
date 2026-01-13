# File: src/iotopen_bridge/converters/mapping/ha_props.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass

from ...models.lynx import FunctionX


@dataclass(frozen=True)
class Semantics:
    component: (
        str  # sensor, binary_sensor, switch, light, cover, climate, number, select, button...
    )
    device_class: str | None = None
    unit_of_measurement: str | None = None
    state_class: str | None = None
    icon: str | None = None
    entity_category: str | None = None

    # Feature flags (used by function_to_entity to expose extra topics)
    supports_brightness: bool = False
    supports_color_temp: bool = False
    supports_cover_position: bool = False
    supports_climate_modes: bool = False
    supports_climate_temperature: bool = False


def infer_semantics(fx: FunctionX) -> Semantics:
    """Infer HA component + key properties from FunctionX.type.

    Conservative: prefer fewer claims over wrong claims.
    """
    t = (getattr(fx, "type", "") or "").strip().lower()

    # ---- explicit components first ----

    # Light
    if t.startswith("light") or t in {"lamp", "dimmer", "bulb"} or "light" in t:
        supports_bri = any(k in t for k in ("dimmer", "brightness", "bri"))
        supports_ct = any(k in t for k in ("color_temp", "colortemp", "ct", "mired", "kelvin"))
        return Semantics(
            component="light", supports_brightness=supports_bri, supports_color_temp=supports_ct
        )

    # Cover
    if t.startswith("cover") or any(
        k in t for k in ("blind", "blinds", "shutter", "curtain", "garage")
    ):
        supports_pos = any(k in t for k in ("position", "percent", "tilt"))
        return Semantics(component="cover", supports_cover_position=supports_pos)

    # Climate
    if t.startswith("climate") or any(k in t for k in ("thermostat", "hvac", "heater", "heatpump")):
        # default to supporting both; it's OK if upstream ignores one path
        return Semantics(
            component="climate",
            supports_climate_modes=True,
            supports_climate_temperature=True,
        )

    # Number
    if t.startswith("number") or any(k in t for k in ("setpoint", "level", "duty", "percent")):
        return Semantics(component="number")

    # Select
    if t.startswith("select") or any(k in t for k in ("mode_select", "profile", "preset")):
        return Semantics(component="select")

    # Button
    if t.startswith("button") or any(k in t for k in ("press", "trigger", "pulse")):
        return Semantics(component="button")

    # ---- existing mappings ----

    # Switches / actuators
    if t in {"switch", "relay", "plug", "outlet"}:
        return Semantics(component="switch")

    # Binary sensors
    if t.startswith(("binary", "alarm", "contact", "motion", "door", "window", "presence")):
        dc = None
        if "motion" in t:
            dc = "motion"
        elif "door" in t:
            dc = "door"
        elif "window" in t:
            dc = "window"
        elif "contact" in t:
            dc = "door"
        return Semantics(component="binary_sensor", device_class=dc)

    # Common sensors
    if "temperature" in t or t in {"temp", "sensor_temperature"}:
        return Semantics(component="sensor", device_class="temperature", unit_of_measurement="°C")
    if "humidity" in t:
        return Semantics(component="sensor", device_class="humidity", unit_of_measurement="%")
    if "power" in t and "alarm" not in t:
        return Semantics(component="sensor", device_class="power", unit_of_measurement="W")
    if "energy" in t:
        return Semantics(
            component="sensor",
            device_class="energy",
            unit_of_measurement="kWh",
            state_class="total_increasing",
        )
    if "pressure" in t:
        return Semantics(component="sensor", device_class="pressure")

    return Semantics(component="sensor")
