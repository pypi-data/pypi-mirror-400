# File: src/iotopen_bridge/controllers/telemetry.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
import json
import logging
import time
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from ..adapters.ha_discovery_publisher import HADiscoveryPublisher
from ..converters.mapping.ha_props import infer_semantics
from ..converters.payload.adapters import (
    DefaultJsonAdapter,
    PayloadAdapter,
    default_adapters_registry,
)
from ..core.event_bus import EventBus
from ..core.mapping_registry import MappingRegistry
from ..core.registry import Registry
from ..models.events import TelemetryEvent

_LOGGER = logging.getLogger(__name__)

_MAX_ATTR_BYTES = 256_000


def _decode_text(payload: bytes) -> str:
    try:
        return payload.decode("utf-8", "ignore").strip()
    except Exception:
        return ""


def _coerce_bytes(v: Any) -> bytes:
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    return str(v).encode("utf-8")


def _try_json_obj(payload: bytes) -> dict[str, Any] | None:
    if payload is None:
        return None
    if len(payload) > _MAX_ATTR_BYTES:
        return None
    s = _decode_text(payload)
    if not s or not s.startswith("{"):
        return None
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _looks_truthy(s: str) -> bool:
    return s in ("on", "true", "t", "yes", "y", "1", "open", "opening")


def _looks_falsy(s: str) -> bool:
    return s in ("off", "false", "f", "no", "n", "0", "closed", "closing")


def _map_onoff_domain(fx: Any, payload: bytes) -> bytes:
    """If fx has state_on/off, publish state in that domain (e.g. 1/0)."""
    state_on = getattr(fx, "state_on", None)
    state_off = getattr(fx, "state_off", None)

    if state_on is None and state_off is None:
        return payload

    with contextlib.suppress(Exception):
        p_txt = _decode_text(payload)
        p_low = p_txt.lower()

        if state_on is not None:
            on_b = _coerce_bytes(state_on)
            if payload == on_b or p_txt == _decode_text(on_b) or _looks_truthy(p_low):
                return on_b

        if state_off is not None:
            off_b = _coerce_bytes(state_off)
            if payload == off_b or p_txt == _decode_text(off_b) or _looks_falsy(p_low):
                return off_b

    return payload


def _iter_function_ids_for_topic(registry: Registry, topic: str) -> Iterable[int]:
    fx_single = registry.get_function_by_topic_read(topic)
    if fx_single is not None:
        try:
            fid = int(getattr(fx_single, "function_id", 0) or 0)
            if fid:
                return (fid,)
        except Exception:
            return ()

    try:
        ids = registry.get_function_ids_by_topic_read(topic)
        return tuple(int(x) for x in ids if int(x) > 0)
    except Exception:
        return ()


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


@dataclass
class TelemetryController:
    registry: Registry
    ha: HADiscoveryPublisher

    # Optional: emit TelemetryEvent for non-MQTT consumers (e.g., HA custom integration).
    bus: EventBus | None = None

    # Optional: align inbound parsing with the same adapter selection logic as commands
    mapping: MappingRegistry | None = None
    adapters: dict[str, PayloadAdapter] | None = None

    # Tests expect retained HA state regardless of upstream retain
    state_retain: bool = True

    def _adapter_for(self, fx: Any) -> PayloadAdapter:
        reg = self.adapters or default_adapters_registry()
        adapter_id = "default"

        fx_raw = _fx_raw(fx)
        with contextlib.suppress(Exception):
            caps = fx_raw.get("capabilities")
            if isinstance(caps, dict) and caps.get("adapter"):
                adapter_id = str(caps["adapter"])

        # mapping registry can override
        if self.mapping is not None:
            with contextlib.suppress(Exception):
                iid = int(getattr(fx, "installation_id", 0) or 0)
                fid = int(getattr(fx, "function_id", 0) or 0)
                if iid and fid:
                    mcaps = self.mapping.caps_for(iid, fid, fx_raw)
                    if getattr(mcaps, "adapter", None):
                        adapter_id = str(mcaps.adapter)

        return reg.get(adapter_id) or DefaultJsonAdapter()

    def handle_message(self, topic: str, payload: bytes, qos: int, retain: bool) -> None:
        topic_s = str(topic or "")
        fids = tuple(_iter_function_ids_for_topic(self.registry, topic_s))
        if not fids:
            return

        for fid in fids:
            fx = self.registry.get_function(fid)
            if fx is None:
                continue

            try:
                iid = int(getattr(fx, "installation_id", 0) or 0)
                fid_i = int(getattr(fx, "function_id", 0) or 0)
            except Exception:
                continue
            if not iid or not fid_i:
                continue

            if self.bus is not None:
                with contextlib.suppress(Exception):
                    self.bus.publish(
                        TelemetryEvent(
                            topic=str(topic_s),
                            installation_id=int(iid),
                            function_id=int(fid_i),
                            qos=int(qos),
                            retain=bool(retain),
                            payload=bytes(payload),
                        )
                    )

            # last_seen
            with contextlib.suppress(Exception):
                self.registry.last_seen[fid_i] = time.time()

            # availability
            with contextlib.suppress(Exception):
                self.ha.publish_entity_availability(iid, fid_i, True)

            sem = infer_semantics(fx)
            base = f"{self.ha.state_prefix}/{iid}/{fid_i}"

            adapter = self._adapter_for(fx)
            keymap: dict[str, bytes] = {}
            try:
                keymap = adapter.upstream_to_ha(payload=payload, fx=fx) or {}
            except Exception:
                keymap = {}

            # Fan-out richer keys (from adapter OR JSON)
            # NOTE: IoT Open commonly sends JSON like {"value": false}. If the adapter
            # doesn't map that to "state" we still want HA base state to track "value".
            obj = _try_json_obj(payload)
            with contextlib.suppress(Exception):
                if obj is not None:
                    for k, v in obj.items():
                        if k not in keymap:
                            keymap[k] = _coerce_bytes(v)

            # Always publish base state (except button)
            if sem.component != "button":
                raw_state = keymap.get("state") or keymap.get("value") or payload
                out_state = _map_onoff_domain(fx, raw_state)
                try:
                    self.ha.publish(f"{base}/state", out_state, int(qos), bool(self.state_retain))
                except Exception as e:
                    _LOGGER.debug("State publish failed topic=%s err=%s", f"{base}/state", e)

            with contextlib.suppress(Exception):
                if sem.component == "light":
                    if "brightness" in keymap:
                        self.ha.publish(
                            f"{base}/state/brightness", keymap["brightness"], int(qos), True
                        )
                    if "color_temp" in keymap:
                        self.ha.publish(
                            f"{base}/state/color_temp", keymap["color_temp"], int(qos), True
                        )

                elif sem.component == "cover":
                    if "position" in keymap:
                        self.ha.publish(
                            f"{base}/state/position", keymap["position"], int(qos), True
                        )

                elif sem.component == "climate":
                    if "mode" in keymap:
                        self.ha.publish(f"{base}/state/mode", keymap["mode"], int(qos), True)
                    if "temperature" in keymap:
                        self.ha.publish(
                            f"{base}/state/temperature", keymap["temperature"], int(qos), True
                        )

            # Attributes (optional)
            if not getattr(self.ha, "attributes_enabled", False):
                continue
            if obj is None:
                continue

            attrs: dict[str, Any] = dict(obj)
            attrs.setdefault("topic_read", topic_s)
            attrs.setdefault("installation_id", iid)
            attrs.setdefault("function_id", fid_i)

            with contextlib.suppress(Exception):
                self.ha.publish_attributes(iid, fid_i, attrs, qos=1, retain=True)
