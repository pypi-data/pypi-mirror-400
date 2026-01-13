# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/ha_discovery/builder.py
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from ..mapping.entities import HAEntitySpec
from .topics import discovery_config_topic


@dataclass(frozen=True)
class DiscoveryMessage:
    topic: str
    payload: dict[str, Any]


def _availability_list(entity: HAEntitySpec) -> list[str]:
    """Normalize availability into a list of topics."""
    av_multi = getattr(entity, "availability_topics", None)
    if isinstance(av_multi, list):
        return [str(t).strip() for t in av_multi if isinstance(t, str) and str(t).strip()]

    av_single = getattr(entity, "availability_topic", None)
    if isinstance(av_single, str) and av_single.strip():
        return [av_single.strip()]

    return []


def _as_str_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v]
    if isinstance(v, tuple):
        return [str(x) for x in v]
    if isinstance(v, set):
        return [str(x) for x in v]
    if isinstance(v, Iterable) and not isinstance(v, (str, bytes, bytearray, dict)):
        return [str(x) for x in v]
    return []


def build_discovery(entity: HAEntitySpec, *, discovery_prefix: str) -> DiscoveryMessage:
    """Build Home Assistant MQTT discovery config (payload + topic) from HAEntitySpec."""
    dp = str(discovery_prefix).strip("/")
    comp = entity.component
    obj = entity.object_id
    topic = discovery_config_topic(dp, comp, obj)

    payload: dict[str, Any] = {
        "name": entity.name,
        "unique_id": entity.unique_id,
        "qos": int(getattr(entity, "qos", 0) or 0),
        "retain": bool(getattr(entity, "retain", False)),
    }

    state_topic = getattr(entity, "state_topic", None)
    if state_topic:
        payload["state_topic"] = state_topic

    dev = getattr(entity, "device", None)
    if dev is not None:
        payload["device"] = {
            "identifiers": list(getattr(dev, "identifiers", []) or []),
            "name": getattr(dev, "name", None),
            "manufacturer": getattr(dev, "manufacturer", None),
            "model": getattr(dev, "model", None),
        }
        sw_version = getattr(dev, "sw_version", None)
        if sw_version:
            payload["device"]["sw_version"] = sw_version

    for k in ("device_class", "unit_of_measurement", "state_class", "icon", "entity_category"):
        v = getattr(entity, k, None)
        if v is not None and v != "":
            payload[k] = v

    json_attrs_topic = getattr(entity, "json_attributes_topic", None)
    if json_attrs_topic:
        payload["json_attributes_topic"] = json_attrs_topic

    av = _availability_list(entity)
    if av:
        payload["payload_available"] = "online"
        payload["payload_not_available"] = "offline"

    if len(av) == 1:
        payload["availability_topic"] = av[0]
    elif len(av) >= 2:
        payload["availability"] = [{"topic": t} for t in av]
        payload["availability_mode"] = getattr(entity, "availability_mode", None) or "all"

    expire_after = getattr(entity, "expire_after_seconds", None)
    if expire_after is not None:
        payload["expire_after"] = int(expire_after)

    if comp == "switch":
        command_topic = getattr(entity, "command_topic", None)
        if not command_topic:
            raise ValueError("switch requires command_topic")
        payload["command_topic"] = command_topic

        p_on = getattr(entity, "payload_on", None)
        p_off = getattr(entity, "payload_off", None)
        if p_on is not None:
            payload["state_on"] = str(p_on)
        if p_off is not None:
            payload["state_off"] = str(p_off)

    elif comp == "binary_sensor":
        # Binary sensors have no command topic. Define which payload means ON/OFF.
        p_on = getattr(entity, "payload_on", None)
        p_off = getattr(entity, "payload_off", None)
        if p_on is not None:
            payload["payload_on"] = str(p_on)
        if p_off is not None:
            payload["payload_off"] = str(p_off)

    elif comp == "light":
        command_topic = getattr(entity, "command_topic", None)
        if not command_topic:
            raise ValueError("light requires command_topic")
        payload["command_topic"] = command_topic

        v = getattr(entity, "brightness_state_topic", None)
        if v:
            payload["brightness_state_topic"] = v
        v = getattr(entity, "brightness_command_topic", None)
        if v:
            payload["brightness_command_topic"] = v

        brightness_scale = getattr(entity, "brightness_scale", None)
        if brightness_scale is not None:
            payload["brightness_scale"] = int(brightness_scale)

        v = getattr(entity, "color_temp_state_topic", None)
        if v:
            payload["color_temp_state_topic"] = v
        v = getattr(entity, "color_temp_command_topic", None)
        if v:
            payload["color_temp_command_topic"] = v

        min_mireds = getattr(entity, "min_mireds", None)
        if min_mireds is not None:
            payload["min_mireds"] = int(min_mireds)

        max_mireds = getattr(entity, "max_mireds", None)
        if max_mireds is not None:
            payload["max_mireds"] = int(max_mireds)

    elif comp == "cover":
        v = getattr(entity, "command_topic", None)
        if v:
            payload["command_topic"] = v
        v = getattr(entity, "position_topic", None)
        if v:
            payload["position_topic"] = v
        v = getattr(entity, "set_position_topic", None)
        if v:
            payload["set_position_topic"] = v

        payload["payload_open"] = getattr(entity, "payload_open", "OPEN")
        payload["payload_close"] = getattr(entity, "payload_close", "CLOSE")
        payload["payload_stop"] = getattr(entity, "payload_stop", "STOP")
        payload["position_open"] = int(getattr(entity, "position_open", 100))
        payload["position_closed"] = int(getattr(entity, "position_closed", 0))

    elif comp == "climate":
        v = getattr(entity, "mode_state_topic", None)
        if v:
            payload["mode_state_topic"] = v
        v = getattr(entity, "mode_command_topic", None)
        if v:
            payload["mode_command_topic"] = v

        modes = getattr(entity, "modes", None)
        if modes is not None:
            payload["modes"] = _as_str_list(modes)

        v = getattr(entity, "temperature_state_topic", None)
        if v:
            payload["temperature_state_topic"] = v
        v = getattr(entity, "temperature_command_topic", None)
        if v:
            payload["temperature_command_topic"] = v

        min_temp = getattr(entity, "min_temp", None)
        if min_temp is not None:
            payload["min_temp"] = float(min_temp)
        max_temp = getattr(entity, "max_temp", None)
        if max_temp is not None:
            payload["max_temp"] = float(max_temp)
        temp_step = getattr(entity, "temp_step", None)
        if temp_step is not None:
            payload["temp_step"] = float(temp_step)

    elif comp == "number":
        command_topic = getattr(entity, "command_topic", None)
        state_topic2 = getattr(entity, "state_topic", None)
        if not command_topic or not state_topic2:
            raise ValueError("number requires command_topic and state_topic")
        payload["command_topic"] = command_topic
        payload["state_topic"] = state_topic2
        payload["min"] = float(getattr(entity, "min_value", 0.0) or 0.0)
        payload["max"] = float(getattr(entity, "max_value", 100.0) or 100.0)
        payload["step"] = float(getattr(entity, "step", 1.0) or 1.0)

        number_mode = getattr(entity, "number_mode", None)
        if number_mode is not None and number_mode != "":
            payload["mode"] = str(number_mode)

    elif comp == "select":
        command_topic = getattr(entity, "command_topic", None)
        state_topic2 = getattr(entity, "state_topic", None)
        if not command_topic or not state_topic2:
            raise ValueError("select requires command_topic and state_topic")
        payload["command_topic"] = command_topic
        payload["state_topic"] = state_topic2
        payload["options"] = _as_str_list(getattr(entity, "options", None) or [])

    elif comp == "button":
        command_topic = getattr(entity, "command_topic", None)
        if not command_topic:
            raise ValueError("button requires command_topic")
        payload["command_topic"] = command_topic
        payload["payload_press"] = getattr(entity, "payload_press", "PRESS")

    extra = getattr(entity, "extra", None)
    if isinstance(extra, dict) and extra:
        payload.update(extra)

    return DiscoveryMessage(topic=topic, payload=payload)
