# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/payload/adapters.py
from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass
from typing import Any, Protocol

Publish = tuple[str, str | bytes, int, bool]


class PayloadAdapter(Protocol):
    """Translate between HA semantic commands and upstream vendor schemas."""

    def ha_to_upstream(self, *, key: str, value: Any, fx: Any) -> list[Publish]: ...

    def upstream_to_ha(self, *, payload: bytes, fx: Any) -> dict[str, bytes]: ...


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


def _stable_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _coerce_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in ("1", "true", "t", "yes", "y", "on", "open")


def _bytes(v: Any) -> bytes:
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    return str(v).encode("utf-8")


def _topic_replace_last_segment(topic: str, new_last: str) -> str:
    parts = [p for p in str(topic or "").split("/") if p]
    if not parts:
        return str(topic or "")
    parts[-1] = str(new_last)
    return "/".join(parts)


def _clamp_int(x: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(x)))


def _kelvin_to_mired(k: int) -> int:
    if k <= 0:
        return 0
    return round(1_000_000 / float(k))


@dataclass
class DefaultJsonAdapter:
    """
    Default adapter:
      - state -> use fx.state_on/state_off if available (else ON/OFF)
      - everything else -> JSON wrapper {"key": value} to fx.topic_set
    """

    qos: int = 1
    retain: bool = False

    def ha_to_upstream(self, *, key: str, value: Any, fx: Any) -> list[Publish]:
        topic = str(getattr(fx, "topic_set", "") or "")
        if not topic:
            return []

        if key == "state":
            on = _coerce_bool(value)
            if on:
                out = getattr(fx, "state_on", None)
                out = out if out is not None else "ON"
            else:
                out = getattr(fx, "state_off", None)
                out = out if out is not None else "OFF"
            return [(topic, str(out), self.qos, self.retain)]

        return [(topic, _stable_json({key: value}), self.qos, self.retain)]

    def upstream_to_ha(self, *, payload: bytes, fx: Any) -> dict[str, bytes]:
        return {"state": payload}


@dataclass
class Zigbee2MQTTAdapter:
    """
    Zigbee2MQTT convention:
      fx.topic_set should point to the Z2M set-topic (commonly "<friendly>/set")
      publishes JSON:
        {"state":"ON"}, {"brightness":128}, {"color_temp":250}, {"position":50}, ...
    """

    qos: int = 1
    retain: bool = False

    # knobs (override via fx.raw["capabilities"]["zigbee2mqtt"])
    brightness_scale: str = "auto"  # "auto" | "0-100" | "0-254"
    color_temp_unit: str = "auto"  # "auto" | "mired" | "kelvin"

    def ha_to_upstream(self, *, key: str, value: Any, fx: Any) -> list[Publish]:
        topic = str(getattr(fx, "topic_set", "") or "")
        if not topic:
            return []

        raw = _fx_raw(fx)
        zcfg: dict[str, Any] = {}
        try:
            zcfg = (raw.get("capabilities") or {}).get("zigbee2mqtt") or {}
        except Exception:
            zcfg = {}

        bscale = str(zcfg.get("brightness_scale") or self.brightness_scale)
        ctunit = str(zcfg.get("color_temp_unit") or self.color_temp_unit)

        payload: dict[str, Any] = {}

        if key == "state":
            payload["state"] = "ON" if _coerce_bool(value) else "OFF"

        elif key == "brightness":
            v = int(value)
            if bscale == "0-100":
                v = _clamp_int(v, 0, 100)
                payload["brightness"] = round(v * 254 / 100)
            elif bscale == "0-254":
                payload["brightness"] = _clamp_int(v, 0, 254)
            else:
                if 0 <= v <= 100:
                    payload["brightness"] = round(v * 254 / 100)
                else:
                    payload["brightness"] = _clamp_int(v, 0, 254)

        elif key == "color_temp":
            v = int(value)
            if ctunit == "kelvin":
                payload["color_temp"] = _kelvin_to_mired(v)
            elif ctunit == "mired":
                payload["color_temp"] = v
            else:
                payload["color_temp"] = _kelvin_to_mired(v) if v >= 1000 else v

        elif key == "position":
            payload["position"] = _clamp_int(int(value), 0, 100)

        elif key == "open":
            payload["state"] = "OPEN" if _coerce_bool(value) else "CLOSE"

        elif key == "mode":
            mode_key = "system_mode"
            with contextlib.suppress(Exception):
                mode_key = str(zcfg.get("mode_key") or mode_key)
            payload[mode_key] = str(value)

        elif key in ("temperature", "target_temperature", "setpoint"):
            temp_key = "current_heating_setpoint"
            with contextlib.suppress(Exception):
                temp_key = str(zcfg.get("setpoint_key") or temp_key)
            payload[temp_key] = float(value)

        else:
            payload[key] = value

        return [(topic, _stable_json(payload), self.qos, self.retain)]

    def upstream_to_ha(self, *, payload: bytes, fx: Any) -> dict[str, bytes]:
        with contextlib.suppress(Exception):
            s = payload.decode("utf-8", "ignore").strip()
            if s.startswith("{") and s.endswith("}"):
                obj = json.loads(s)
                if isinstance(obj, dict):
                    out: dict[str, bytes] = {}
                    for k in (
                        "state",
                        "brightness",
                        "color_temp",
                        "position",
                        "system_mode",
                        "mode",
                        "current_heating_setpoint",
                    ):
                        if k in obj:
                            out[k] = _bytes(obj[k])
                    if out:
                        return out
        return {"state": payload}


@dataclass
class TasmotaAdapter:
    """
    Tasmota MQTT:
      fx.topic_set is treated as a command base (e.g. "cmnd/<dev>/{cmd}" or "cmnd/<dev>/POWER").
      Derives commands by replacing last segment unless "{cmd}" template is used.
    """

    qos: int = 1
    retain: bool = False

    def ha_to_upstream(self, *, key: str, value: Any, fx: Any) -> list[Publish]:
        base = str(getattr(fx, "topic_set", "") or "")
        if not base:
            return []

        raw = _fx_raw(fx)
        tcfg: dict[str, Any] = {}
        try:
            tcfg = (raw.get("capabilities") or {}).get("tasmota") or {}
        except Exception:
            tcfg = {}

        def cmd_topic(cmd: str) -> str:
            if "{cmd}" in base:
                return base.replace("{cmd}", cmd)
            return _topic_replace_last_segment(base, cmd)

        if key == "state":
            pl = "ON" if _coerce_bool(value) else "OFF"
            return [(cmd_topic("POWER"), pl, self.qos, self.retain)]

        if key == "brightness":
            v = _clamp_int(int(value), 0, 100)
            cmd = str(tcfg.get("brightness_cmd") or "Dimmer")
            return [(cmd_topic(cmd), str(v), self.qos, self.retain)]

        if key == "color_temp":
            v = int(value)
            if v >= 1000:
                v = _kelvin_to_mired(v)
            cmd = str(tcfg.get("ct_cmd") or "CT")
            return [(cmd_topic(cmd), str(v), self.qos, self.retain)]

        if key == "position":
            idx = tcfg.get("shutter_index")
            cmd = "ShutterPosition"
            if idx is not None:
                cmd = f"ShutterPosition{int(idx)}"
            cmd = str(tcfg.get("position_cmd") or cmd)
            v = _clamp_int(int(value), 0, 100)
            return [(cmd_topic(cmd), str(v), self.qos, self.retain)]

        if key == "open":
            return self.ha_to_upstream(
                key="position", value=(100 if _coerce_bool(value) else 0), fx=fx
            )

        return [(base, _stable_json({key: value}), self.qos, self.retain)]

    def upstream_to_ha(self, *, payload: bytes, fx: Any) -> dict[str, bytes]:
        return {"state": payload}


@dataclass
class ShellyGen2RpcAdapter:
    """
    Shelly Gen2/Plus JSON-RPC over MQTT.

    Expects capability:
      fx.raw["capabilities"]["shelly"] = {
        "rpc_topic": ".../rpc",
        "kind": "switch" | "light" | "cover",
        "id": 0,
        "src": "iotopen-bridge",
      }
    """

    qos: int = 1
    retain: bool = False

    def ha_to_upstream(self, *, key: str, value: Any, fx: Any) -> list[Publish]:
        raw = _fx_raw(fx)
        scfg: dict[str, Any] = {}
        try:
            scfg = (raw.get("capabilities") or {}).get("shelly") or {}
        except Exception:
            scfg = {}

        topic = str(scfg.get("rpc_topic") or getattr(fx, "topic_set", "") or "")
        if not topic:
            return []

        kind = str(scfg.get("kind") or "switch").lower()
        chan_id = int(scfg.get("id") or 0)
        src = str(scfg.get("src") or "iotopen-bridge")

        method: str
        params: dict[str, Any] = {"id": chan_id}

        if kind == "switch":
            method = "Switch.Set"
            if key == "state":
                params["on"] = _coerce_bool(value)
            else:
                params[key] = value

        elif kind == "light":
            method = "Light.Set"
            if key == "state":
                params["on"] = _coerce_bool(value)
            elif key == "brightness":
                params["brightness"] = _clamp_int(int(value), 0, 100)
            elif key == "color_temp":
                v = int(value)
                if 0 < v < 1000:
                    v = round(1_000_000 / float(v))  # mired -> kelvin
                params["temp"] = v
            else:
                params[key] = value

        elif kind == "cover":
            method = "Cover.Set"
            if key == "position":
                params["pos"] = _clamp_int(int(value), 0, 100)
            elif key == "open":
                params["pos"] = 100 if _coerce_bool(value) else 0
            else:
                params[key] = value

        else:
            method = str(scfg.get("method") or "Sys.SetConfig")
            params[key] = value

        req = {"id": 1, "src": src, "method": method, "params": params}
        return [(topic, _stable_json(req), self.qos, self.retain)]

    def upstream_to_ha(self, *, payload: bytes, fx: Any) -> dict[str, bytes]:
        with contextlib.suppress(Exception):
            s = payload.decode("utf-8", "ignore").strip()
            if s.startswith("{") and s.endswith("}"):
                obj = json.loads(s)
                if isinstance(obj, dict):
                    out: dict[str, bytes] = {}
                    params = obj.get("params")
                    if isinstance(params, dict):
                        for k in ("on", "brightness", "temp", "pos"):
                            if k in params:
                                out[k] = _bytes(params[k])
                    if out:
                        return out
        return {"state": payload}


def default_adapters_registry() -> dict[str, PayloadAdapter]:
    return {
        "default": DefaultJsonAdapter(),
        "zigbee2mqtt": Zigbee2MQTTAdapter(),
        "tasmota": TasmotaAdapter(),
        "shelly_rpc": ShellyGen2RpcAdapter(),
    }
