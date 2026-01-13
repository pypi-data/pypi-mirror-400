# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/mapping/function_to_entity.py
from __future__ import annotations

from dataclasses import replace
from typing import Any

from ...core.mapping_registry import MappingRegistry
from ...models.lynx import FunctionX
from .entities import HADeviceInfo, HAEntitySpec
from .ha_props import Semantics, infer_semantics

# Prefer existing helpers if present (your tests already use discovery_object_id_from_unique_id)
try:
    from ...core.ids import discovery_object_id_from_unique_id, stable_device_id, stable_entity_name
except Exception:  # pragma: no cover

    def discovery_object_id_from_unique_id(unique_id: str, *, max_len: int = 64) -> str:
        # conservative fallback: "iotopen_2222_508312"
        parts = [p for p in unique_id.replace("iotopen:", "").split(":") if p]
        if len(parts) == 2 and all(x.isdigit() for x in parts):
            out = f"iotopen_{parts[0]}_{parts[1]}"
        else:
            out = unique_id.replace(":", "_").replace("/", "_")
        return out[: int(max_len)] if max_len and len(out) > int(max_len) else out

    def stable_device_id(installation_id: int, *, prefix: str = "iotopen") -> str:
        return f"{prefix}:{int(installation_id)}"

    def stable_entity_name(friendly_name: str | None, fallback: str) -> str:
        s = (friendly_name or "").strip()
        return s if s else fallback


def _fx_raw(fx: Any) -> dict[str, Any]:
    raw = getattr(fx, "raw", None)
    if isinstance(raw, dict):
        return raw
    extra = getattr(fx, "extra", None)
    if isinstance(extra, dict):
        return extra
    meta = getattr(fx, "meta", None)
    if isinstance(meta, dict):
        return meta
    return {}


def _fx_caps(fx: Any) -> dict[str, Any]:
    """Best-effort capability dict from fx.raw["capabilities"] (if present)."""
    raw = _fx_raw(fx)
    caps = raw.get("capabilities")
    return caps if isinstance(caps, dict) else {}


def _cap_get(caps: Any, key: str, default: Any = None) -> Any:
    if isinstance(caps, dict):
        return caps.get(key, default)
    return getattr(caps, key, default)


def _apply_discovery_overrides(ent: HAEntitySpec, disc_over: Any | None) -> HAEntitySpec:
    if disc_over is None:
        return ent

    # Entity identity
    if getattr(disc_over, "name", None):
        ent = replace(ent, name=str(disc_over.name))
    if getattr(disc_over, "object_id", None):
        ent = replace(ent, object_id=str(disc_over.object_id))

    # Device block
    dev = getattr(ent, "device", None)
    if dev is not None:
        dev_name = getattr(disc_over, "device_name", None)
        sug_area = getattr(disc_over, "suggested_area", None)
        cfg_url = getattr(disc_over, "configuration_url", None)
        if dev_name:
            dev = replace(dev, name=str(dev_name))
        if sug_area is not None:
            dev = replace(dev, suggested_area=str(sug_area) if sug_area else None)
        if cfg_url is not None:
            dev = replace(dev, configuration_url=str(cfg_url) if cfg_url else None)
        ent = replace(ent, device=dev)

    # MQTT knobs
    if getattr(disc_over, "expire_after_seconds", None) is not None:
        ent = replace(ent, expire_after_seconds=int(disc_over.expire_after_seconds))
    if getattr(disc_over, "qos", None) is not None:
        ent = replace(ent, qos=int(disc_over.qos))
    if getattr(disc_over, "retain", None) is not None:
        ent = replace(ent, retain=bool(disc_over.retain))

    # Advanced: merge arbitrary discovery keys
    extra = getattr(disc_over, "extra", None)
    if isinstance(extra, dict) and extra:
        merged = dict(getattr(ent, "extra", None) or {})
        merged.update(extra)
        ent = replace(ent, extra=merged)

    return ent


def function_to_entity(
    fx: FunctionX,
    *,
    ha_state_prefix: str,
    mapping: MappingRegistry | None = None,
    availability_topics: list[str] | None = None,
    availability_mode: str = "all",
    attributes_enabled: bool = True,
    expire_after_seconds: int | None = None,
) -> HAEntitySpec:
    """Map FunctionX -> HAEntitySpec.

    Topic scheme (HA-side):
      Base: <state_prefix>/<iid>/<fid>

      State:
        <base>/state
        plus component sub-states (published by TelemetryController):
          light:   <base>/state/brightness, <base>/state/color_temp
          cover:   <base>/state/position
          climate: <base>/state/mode, <base>/state/temperature

      Commands (HA -> bridge):
        switch legacy: <base>/set        (ON/OFF)
        extended:      <base>/<kind>/set (brightness/color_temp/position/mode/temperature/etc)
    """
    iid = int(getattr(fx, "installation_id", 0) or 0)
    fid = int(getattr(fx, "function_id", 0) or 0)

    unique_id = f"iotopen:{iid}:{fid}"
    object_id = discovery_object_id_from_unique_id(unique_id)

    fallback_name = f"IoT Open {iid} {fid}"
    name = stable_entity_name(getattr(fx, "friendly_name", None), fallback_name)

    state_prefix = str(ha_state_prefix).strip("/")
    base = f"{state_prefix}/{iid}/{fid}"

    # Device info (stable, unless overridden)
    device = HADeviceInfo(
        identifiers=[stable_device_id(iid)],
        name=f"IoT Open Installation {iid}",
        manufacturer="IoT Open",
        model="Lynx",
    )
    fx_raw = _fx_raw(fx)

    # ---- semantics + caps (default inference + optional overrides) ----
    sem: Semantics = infer_semantics(fx)
    disc_over = None
    caps: Any

    if mapping is not None:
        caps = mapping.caps_for(iid, fid, fx_raw)
        sem_over = mapping.semantics_for(iid, fid, fx_raw)
        disc_over = mapping.discovery_for(iid, fid, fx_raw)

        # Optional component override: if provided, it becomes authoritative.
        comp_over = (getattr(caps, "component", None) or "").strip().lower()
        if comp_over:
            sem = Semantics(component=comp_over)

        # Semantics overrides
        if getattr(sem_over, "device_class", None):
            sem = replace(sem, device_class=str(sem_over.device_class))
        if getattr(sem_over, "state_class", None):
            sem = replace(sem, state_class=str(sem_over.state_class))
        if getattr(sem_over, "unit", None):
            sem = replace(sem, unit_of_measurement=str(sem_over.unit))
        if getattr(sem_over, "icon", None):
            sem = replace(sem, icon=str(sem_over.icon))
    else:
        caps = _fx_caps(fx)

    # Base topics (depends on final component)
    state_topic = None if sem.component == "button" else f"{base}/state"
    attrs_topic = f"{base}/attributes" if attributes_enabled else None

    def _payload_str(v: Any | None) -> str | None:
        if v is None:
            return None
        try:
            return str(v)
        except Exception:
            return None

    # Minimal entity; component-specific fields get added below.
    ent = HAEntitySpec(
        component=sem.component,
        unique_id=unique_id,
        object_id=object_id,
        name=name,
        state_topic=state_topic,
        json_attributes_topic=attrs_topic,
        availability_topics=list(availability_topics or []),
        availability_mode=str(availability_mode or "all"),
        device=device,
        device_class=sem.device_class,
        unit_of_measurement=sem.unit_of_measurement,
        state_class=sem.state_class,
        icon=sem.icon,
        entity_category=sem.entity_category,
        expire_after_seconds=expire_after_seconds,
        qos=1,
        retain=True,
    )

    # Apply discovery overrides early so object_id/name/device name are correct for all components.
    ent = _apply_discovery_overrides(ent, disc_over)

    # ---- component specifics ----

    if sem.component == "switch":
        ent = replace(
            ent,
            command_topic=f"{base}/set",
            payload_on=_payload_str(getattr(fx, "state_on", None)),
            payload_off=_payload_str(getattr(fx, "state_off", None)),
        )
        return ent

    if sem.component == "binary_sensor":
        # Binary sensors have no command topic; we only need to tell HA what
        # payload represents ON/OFF (IoT Open commonly uses 1/0, true/false, etc.).
        ent = replace(
            ent,
            payload_on=_payload_str(getattr(fx, "state_on", None)),
            payload_off=_payload_str(getattr(fx, "state_off", None)),
        )
        return ent

    if sem.component == "light":
        ent = replace(ent, command_topic=f"{base}/set")

        if bool(getattr(sem, "supports_brightness", False)) or bool(
            _cap_get(caps, "brightness", False)
        ):
            ent = replace(
                ent,
                brightness_state_topic=f"{base}/state/brightness",
                brightness_command_topic=f"{base}/brightness/set",
                brightness_scale=int(_cap_get(caps, "brightness_scale", 255) or 255),
            )

        if bool(getattr(sem, "supports_color_temp", False)) or bool(
            _cap_get(caps, "color_temp", False)
        ):
            ent = replace(
                ent,
                color_temp_state_topic=f"{base}/state/color_temp",
                color_temp_command_topic=f"{base}/color_temp/set",
                min_mireds=_cap_get(caps, "color_temp_min"),
                max_mireds=_cap_get(caps, "color_temp_max"),
            )
        return ent

    if sem.component == "cover":
        if bool(getattr(sem, "supports_cover_position", False)) or bool(
            _cap_get(caps, "position", False)
        ):
            ent = replace(
                ent,
                position_topic=f"{base}/state/position",
                set_position_topic=f"{base}/position/set",
            )
        ent = replace(ent, command_topic=f"{base}/set")
        return ent

    if sem.component == "climate":
        ent = replace(
            ent,
            mode_state_topic=f"{base}/state/mode",
            mode_command_topic=f"{base}/mode/set",
            temperature_state_topic=f"{base}/state/temperature",
            temperature_command_topic=f"{base}/temperature/set",
        )
        modes = _cap_get(caps, "modes")
        if isinstance(modes, list):
            ent = replace(ent, modes=[str(x) for x in modes])

        vmin = _cap_get(caps, "min")
        vmax = _cap_get(caps, "max")
        vstep = _cap_get(caps, "step")
        if vmin is not None:
            ent = replace(ent, min_temp=float(vmin))
        if vmax is not None:
            ent = replace(ent, max_temp=float(vmax))
        if vstep is not None:
            ent = replace(ent, temp_step=float(vstep))
        return ent

    if sem.component == "number":
        ent = replace(
            ent,
            command_topic=f"{base}/value/set",
            state_topic=f"{base}/state",
        )
        vmin = _cap_get(caps, "min")
        vmax = _cap_get(caps, "max")
        vstep = _cap_get(caps, "step")
        if vmin is not None:
            ent = replace(ent, min_value=float(vmin))
        if vmax is not None:
            ent = replace(ent, max_value=float(vmax))
        if vstep is not None:
            ent = replace(ent, step=float(vstep))
        return ent

    if sem.component == "select":
        ent = replace(
            ent,
            command_topic=f"{base}/option/set",
            state_topic=f"{base}/state",
        )
        options = _cap_get(caps, "options")
        if isinstance(options, list):
            ent = replace(ent, options=[str(x) for x in options])
        return ent

    if sem.component == "button":
        ent = replace(ent, command_topic=f"{base}/press/set", state_topic=None)
        return ent

    return ent
