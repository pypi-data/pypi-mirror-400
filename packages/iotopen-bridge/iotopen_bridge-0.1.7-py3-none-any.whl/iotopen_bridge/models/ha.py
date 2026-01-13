# File: src/iotopen_bridge/models/ha.py
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _drop_none(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


@dataclass(frozen=True)
class HADeviceInfo:
    """Device registry context for HA discovery."""

    identifiers: list[str]
    name: str
    manufacturer: str = "IoT Open"
    model: str = "Lynx"
    sw_version: str | None = None
    hw_version: str | None = None
    serial_number: str | None = None
    suggested_area: str | None = None
    configuration_url: str | None = None
    via_device: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "identifiers": list(self.identifiers),
                "name": self.name,
                "manufacturer": self.manufacturer,
                "model": self.model,
                "sw_version": self.sw_version,
                "hw_version": self.hw_version,
                "serial_number": self.serial_number,
                "suggested_area": self.suggested_area,
                "configuration_url": self.configuration_url,
                "via_device": self.via_device,
            }
        )


@dataclass(frozen=True)
class HAEntitySpec:
    """Internal entity spec used by mapping + discovery builder.

    Keep this as the single source of truth for what the discovery builder can consume.
    """

    # identity
    component: str
    unique_id: str
    object_id: str
    name: str | None = None

    # topics
    state_topic: str | None = None
    command_topic: str | None = None
    json_attributes_topic: str | None = None

    # availability (bridge uses list-of-topics pattern)
    availability_topics: list[str] = field(default_factory=list)
    availability_mode: str = "all"

    # device + semantics
    device: HADeviceInfo | None = None
    device_class: str | None = None
    unit_of_measurement: str | None = None
    state_class: str | None = None
    icon: str | None = None
    entity_category: str | None = None

    # qos/retain & expiry
    qos: int = 1
    retain: bool = True
    expire_after_seconds: int | None = None

    # switch payload mapping
    payload_on: Any | None = None
    payload_off: Any | None = None

    # light extras
    brightness_state_topic: str | None = None
    brightness_command_topic: str | None = None
    brightness_scale: int | None = None

    color_temp_state_topic: str | None = None
    color_temp_command_topic: str | None = None
    min_mireds: Any | None = None
    max_mireds: Any | None = None

    # cover extras
    position_topic: str | None = None
    set_position_topic: str | None = None

    # climate extras
    mode_state_topic: str | None = None
    mode_command_topic: str | None = None
    temperature_state_topic: str | None = None
    temperature_command_topic: str | None = None
    modes: list[str] | None = None
    min_temp: float | None = None
    max_temp: float | None = None
    temp_step: float | None = None

    # number extras
    min_value: float | None = None
    max_value: float | None = None
    step: float | None = None

    # select extras
    options: list[str] | None = None

    # escape hatch
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "component": self.component,
            "unique_id": self.unique_id,
            "object_id": self.object_id,
            "name": self.name,
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "json_attributes_topic": self.json_attributes_topic,
            "availability_topics": list(self.availability_topics),
            "availability_mode": self.availability_mode,
            "device": self.device.to_dict() if self.device else None,
            "device_class": self.device_class,
            "unit_of_measurement": self.unit_of_measurement,
            "state_class": self.state_class,
            "icon": self.icon,
            "entity_category": self.entity_category,
            "qos": int(self.qos),
            "retain": bool(self.retain),
            "expire_after_seconds": self.expire_after_seconds,
            "payload_on": self.payload_on,
            "payload_off": self.payload_off,
            "brightness_state_topic": self.brightness_state_topic,
            "brightness_command_topic": self.brightness_command_topic,
            "brightness_scale": self.brightness_scale,
            "color_temp_state_topic": self.color_temp_state_topic,
            "color_temp_command_topic": self.color_temp_command_topic,
            "min_mireds": self.min_mireds,
            "max_mireds": self.max_mireds,
            "position_topic": self.position_topic,
            "set_position_topic": self.set_position_topic,
            "mode_state_topic": self.mode_state_topic,
            "mode_command_topic": self.mode_command_topic,
            "temperature_state_topic": self.temperature_state_topic,
            "temperature_command_topic": self.temperature_command_topic,
            "modes": list(self.modes) if isinstance(self.modes, list) else None,
            "min_temp": self.min_temp,
            "max_temp": self.max_temp,
            "temp_step": self.temp_step,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "step": self.step,
            "options": list(self.options) if isinstance(self.options, list) else None,
            "extra": dict(self.extra or {}),
        }
        # keep availability_topics even if empty (it's structural), drop other Nones
        out = _drop_none(d)
        if "availability_topics" not in out:
            out["availability_topics"] = []
        return out


@dataclass(frozen=True)
class DiscoveryPayload:
    topic: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"topic": self.topic, "payload": dict(self.payload)}


# Backwards-friendly aliases (nice names, but keep HA* as canonical for the rest of the codebase)
HaDeviceSpec = HADeviceInfo
HaEntitySpec = HAEntitySpec
