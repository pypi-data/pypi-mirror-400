# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/core/mapping_registry.py
from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # PyYAML already in deps


@dataclass(frozen=True)
class FunctionCaps:
    """Per-function capability/capability-override model.

    Sources (merge order):
      1) sidecar file (MappingRegistry path)
      2) fx_raw["capabilities"]

    NOTE: Keep this intentionally explicit: *no inference* here.
    """

    # Optional component override for discovery/mapping (e.g. "switch", "light").
    # If None, the bridge will infer from FunctionX.type.
    component: str | None = None

    # Light
    brightness: bool = False
    brightness_scale: int = 255
    color_temp: bool = False
    color_temp_min: int | None = None
    color_temp_max: int | None = None

    # Cover
    position: bool = False

    # Climate
    modes: list[str] | None = None

    # Number/select (optional future knobs)
    min: float | None = None
    max: float | None = None
    step: float | None = None

    # Payload adapter id (matches converters.payload.adapters registry keys)
    # Payload adapter id (matches converters.payload.adapters registry keys)
    # If None, the bridge will use the default adapter.
    adapter: str | None = None


@dataclass(frozen=True)
class SemanticsOverride:
    """Overrides for HA semantics to prevent wrong device_class/state_class/unit/icon.

    Sources (merge order):
      1) sidecar file
      2) fx_raw["semantics"]
    """

    device_class: str | None = None
    state_class: str | None = None
    unit: str | None = None
    icon: str | None = None


@dataclass(frozen=True)
class DiscoveryOverride:
    """Overrides for MQTT discovery fields to avoid any HA-side YAML/customization.

    Sources (merge order):
      1) sidecar file
      2) fx_raw["discovery"]
    """

    # Entity identity
    name: str | None = None
    object_id: str | None = None

    # Device block overrides
    device_name: str | None = None
    suggested_area: str | None = None
    configuration_url: str | None = None

    # MQTT knobs
    expire_after_seconds: int | None = None
    qos: int | None = None
    retain: bool | None = None

    # Freeform discovery keys to merge at the end (advanced use)
    extra: dict[str, Any] | None = None


class MappingRegistry:
    """Loads optional sidecar config and resolves per-function capabilities/semantics.

    Sidecar format (YAML or JSON), recommended structure:

    capabilities:
      "2222:508312":
        component: "switch"
        adapter: "zigbee2mqtt"
        brightness: true
        brightness_scale: 254

    semantics:
      "2222:123":
        device_class: "power"
        state_class: "measurement"
        unit: "W"
        icon: "mdi:flash"

    discovery:
      "2222:508312":
        name: "Kitchen Plug"
        suggested_area: "Kitchen"
        expire_after_seconds: 600
        extra:
          enabled_by_default: true
    """

    def __init__(self, path: str | None) -> None:
        self._data: dict[str, Any] = {}
        self._path: str | None = path
        if path:
            self._data = self._load(path)

    def _load(self, path: str) -> dict[str, Any]:
        p = Path(path)
        if not p.exists():
            return {}

        text = p.read_text(encoding="utf-8")
        suffix = p.suffix.lower()

        if suffix == ".json":
            obj = json.loads(text)
            return obj if isinstance(obj, dict) else {}

        # Default to YAML for everything else (.yml/.yaml/.conf)
        obj = yaml.safe_load(text) or {}
        return obj if isinstance(obj, dict) else {}

    def reload(self) -> None:
        """Reload the sidecar file (best-effort)."""
        if not self._path:
            self._data = {}
            return
            # keep last good config
        with contextlib.suppress(Exception):
            self._data = self._load(self._path)

    def _key(self, installation_id: int, function_id: int) -> str:
        return f"{int(installation_id)}:{int(function_id)}"

    @staticmethod
    def _as_dict(v: Any) -> dict[str, Any]:
        return v if isinstance(v, dict) else {}

    @staticmethod
    def _filter_known_fields(model_cls: Any, d: dict[str, Any]) -> dict[str, Any]:
        allowed = set(getattr(model_cls, "__annotations__", {}).keys())
        return {k: v for k, v in d.items() if k in allowed}

    def caps_for(
        self, installation_id: int, function_id: int, fx_raw: dict[str, Any]
    ) -> FunctionCaps:
        """Resolve FunctionCaps for a given iid/fid and raw metadata."""
        merged: dict[str, Any] = {}

        # 1) sidecar
        sidecar_caps = self._as_dict(
            self._as_dict(self._data.get("capabilities")).get(
                self._key(installation_id, function_id)
            )
        )
        merged.update(sidecar_caps)

        # 2) fx.raw["capabilities"]
        raw_caps = self._as_dict(self._as_dict(fx_raw).get("capabilities"))
        merged.update(raw_caps)

        merged = self._filter_known_fields(FunctionCaps, merged)

        try:
            return FunctionCaps(**merged)
        except Exception:
            # If the merged dict is invalid (bad types), fall back to defaults.
            # You can add stricter validation later if desired.
            return FunctionCaps()

    def semantics_for(
        self, installation_id: int, function_id: int, fx_raw: dict[str, Any]
    ) -> SemanticsOverride:
        """Resolve SemanticsOverride for a given iid/fid and raw metadata."""
        merged: dict[str, Any] = {}

        # 1) sidecar
        sidecar = self._as_dict(
            self._as_dict(self._data.get("semantics")).get(self._key(installation_id, function_id))
        )
        merged.update(sidecar)

        # 2) fx.raw["semantics"]
        raw_rules = self._as_dict(self._as_dict(fx_raw).get("semantics"))
        merged.update(raw_rules)

        # Build explicitly (avoid **unknown keys)
        try:
            return SemanticsOverride(
                device_class=merged.get("device_class"),
                state_class=merged.get("state_class"),
                unit=merged.get("unit"),
                icon=merged.get("icon"),
            )
        except Exception:
            return SemanticsOverride()

    def discovery_for(
        self, installation_id: int, function_id: int, fx_raw: dict[str, Any]
    ) -> DiscoveryOverride:
        """Resolve DiscoveryOverride for a given iid/fid and raw metadata."""
        merged: dict[str, Any] = {}

        sidecar = self._as_dict(
            self._as_dict(self._data.get("discovery")).get(self._key(installation_id, function_id))
        )
        merged.update(sidecar)

        raw_rules = self._as_dict(self._as_dict(fx_raw).get("discovery"))
        merged.update(raw_rules)

        extra = merged.get("extra")
        if extra is not None and not isinstance(extra, dict):
            extra = None

        try:
            return DiscoveryOverride(
                name=merged.get("name"),
                object_id=merged.get("object_id"),
                device_name=merged.get("device_name"),
                suggested_area=merged.get("suggested_area"),
                configuration_url=merged.get("configuration_url"),
                expire_after_seconds=merged.get("expire_after_seconds"),
                qos=merged.get("qos"),
                retain=merged.get("retain"),
                extra=extra,
            )
        except Exception:
            return DiscoveryOverride()
