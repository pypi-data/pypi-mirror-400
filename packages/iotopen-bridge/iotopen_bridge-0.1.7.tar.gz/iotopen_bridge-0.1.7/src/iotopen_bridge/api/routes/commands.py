# File: src/iotopen_bridge/controllers/commands.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
import json
import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import RLock
from typing import Any

from ...converters.mapping.ha_props import infer_semantics
from ...converters.normalize.bool import to_bool
from ...core.errors import PolicyDenied
from ...core.event_bus import EventBus
from ...core.registry import Registry
from ...models.events import CommandEvent
from ...models.lynx import FunctionX
from ...security.authz.policy import PolicyEngine
from ...security.crypto.envelope import EnvelopeSettings, unwrap_command
from ...security.crypto.envelope_store import EnvelopeNonceStore

PublishFn = Callable[[str, str | bytes, int, bool], None]
_LOGGER = logging.getLogger(__name__)

_QOS: int = 1
_RETAIN: bool = False


def _encode_payload(value: Any) -> str | bytes:
    """Encode payload for MQTT publish.

    Notes:
    - For dict/list we emit compact JSON.
    - For primitive types we emit str(value).
    - For bytes-like we pass bytes.
    """
    if value is None:
        return ""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _stable_json(value: Any) -> str:
    try:
        return json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        )
    except Exception:
        return str(value)


def _extract_text_any(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip()
    if isinstance(value, (dict, list)):
        return _stable_json(value)
    return str(value).strip()


def _extract_bool_any(value: Any) -> bool | None:
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if float(value) == 0.0:
            return False
        if float(value) == 1.0:
            return True

    if isinstance(value, (bytes, str)):
        s = _extract_text_any(value)
        b = to_bool(s)
        if b is not None:
            return bool(b)

        if s.startswith("{") and s.endswith("}"):
            try:
                obj = json.loads(s)
            except Exception:
                return None
            return _extract_bool_any(obj)

        return None

    if isinstance(value, dict):
        for key in ("state", "on", "value", "enabled", "press"):
            if key in value:
                return _extract_bool_any(value.get(key))
    return None


def _extract_int_any(value: Any) -> int | None:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        try:
            return int(value)
        except Exception:
            return None
    if isinstance(value, (bytes, str)):
        s = _extract_text_any(value)
        try:
            return int(float(s))
        except Exception:
            if s.startswith("{") and s.endswith("}"):
                try:
                    obj = json.loads(s)
                except Exception:
                    return None
                return _extract_int_any(obj)
            return None
    if isinstance(value, dict):
        for key in ("value", "brightness", "color_temp", "position", "temperature"):
            if key in value:
                return _extract_int_any(value.get(key))
    return None


def _extract_float_any(value: Any) -> float | None:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        try:
            return float(value)
        except Exception:
            return None
    if isinstance(value, (bytes, str)):
        s = _extract_text_any(value)
        try:
            return float(s)
        except Exception:
            if s.startswith("{") and s.endswith("}"):
                try:
                    obj = json.loads(s)
                except Exception:
                    return None
                return _extract_float_any(obj)
            return None
    if isinstance(value, dict):
        for key in ("value", "temperature"):
            if key in value:
                return _extract_float_any(value.get(key))
    return None


def _coerce_numeric(value: Any) -> int | float | None:
    """Best-effort numeric coercion used for Lynx /set topics."""
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return float(value)

    if isinstance(value, (bytes, str)):
        s = _extract_text_any(value)
        try:
            f = float(s)
        except Exception:
            return None
        if f.is_integer():
            return int(f)
        return f

    if isinstance(value, dict):
        # Common patterns: {"value": ...}, {"state": ...}, {"on": ...}
        for k in ("value", "state", "on"):
            if k in value:
                return _coerce_numeric(value.get(k))
        # If dict is a “single numeric field” (e.g. {"brightness": 120}), take it.
        for k in ("brightness", "color_temp", "position", "temperature", "level"):
            if k in value:
                return _coerce_numeric(value.get(k))
    return None


def _is_set_topic(topic: str) -> bool:
    t = str(topic or "")
    return "/set/" in f"/{t.strip('/')}/"


def _is_cmd_topic(topic: str) -> bool:
    t = str(topic or "")
    return "/cmd/" in f"/{t.strip('/')}/"


def _switch_publish_value(fx: FunctionX, on: bool) -> int | float:
    """Preferred mapping for boolean actuation:
    - Use FunctionX.state_on/state_off if provided (supports 255/0, etc)
    - Otherwise default to 1/0
    """
    raw = fx.state_on if on else fx.state_off
    n = _coerce_numeric(raw)
    if n is None:
        return 1 if on else 0
    return n


def _lynx_value_message(value: Any) -> dict[str, Any]:
    """Lynx MQTT ValueMessage for /set topics: {"value": <number>}."""
    n = _coerce_numeric(value)
    if n is None:
        raise ValueError("non_numeric_value_for_set_topic")
    return {"value": n}


@dataclass
class CommandsController:
    registry: Registry
    bus: EventBus
    policy: PolicyEngine
    mqtt_publish: PublishFn

    # ---- optional signed-command envelope verification (off by default) ----
    envelope_settings: EnvelopeSettings = field(default_factory=EnvelopeSettings.from_env)
    nonce_store_path: str | None = None

    _nonce_store: EnvelopeNonceStore | None = field(default=None, init=False, repr=False)
    _nonce_mem: dict[tuple[str, str], int] = field(default_factory=dict, init=False, repr=False)
    _nonce_lock: RLock = field(default_factory=RLock, init=False, repr=False)

    def __post_init__(self) -> None:
        if not getattr(self.envelope_settings, "enabled", False):
            return

        db_path = (
            (self.nonce_store_path or "").strip()
            or (os.environ.get("IOTOPEN_BRIDGE_NONCE_DB_PATH") or "").strip()
            or (os.environ.get("IOTOPEN_BRIDGE_SQLITE_PATH") or "").strip()
            or (os.environ.get("IOTOPEN_BRIDGE_STORAGE_PATH") or "").strip()
        )
        if not db_path:
            _LOGGER.debug(
                "Command signing enabled but no nonce DB path configured; using in-memory replay cache."
            )
            return

        try:
            self._nonce_store = EnvelopeNonceStore(db_path)
        except Exception as e:
            _LOGGER.warning(
                "Failed to init EnvelopeNonceStore (%s). Falling back to in-memory replay cache.", e
            )

    def _emit(
        self, *, function_id: int, topic: str, value: Any, ok: bool, error: str | None = None
    ) -> None:
        with contextlib.suppress(Exception):
            self.bus.publish(
                CommandEvent(
                    function_id=int(function_id),
                    topic=str(topic or ""),
                    value=value,
                    ok=bool(ok),
                    error=(str(error) if error else None),
                )
            )

    def _nonce_seen(self, kid: str, nonce: str, ts: int, ttl_seconds: int) -> bool:
        if self._nonce_store is not None:
            return bool(self._nonce_store.nonce_seen(kid, nonce, ts, ttl_seconds))

        now = int(time.time())
        expires = int(max(now, int(ts or 0)) + int(ttl_seconds))
        key = (str(kid or "default"), str(nonce or ""))

        with self._nonce_lock:
            if self._nonce_mem:
                for k, exp in list(self._nonce_mem.items()):
                    if exp <= now:
                        self._nonce_mem.pop(k, None)

            if key in self._nonce_mem:
                return True

            self._nonce_mem[key] = expires
            return False

    def _unwrap_if_needed(self, payload: bytes, *, fx: FunctionX) -> Any:
        if not getattr(self.envelope_settings, "enabled", False):
            return payload

        res = unwrap_command(
            payload,
            settings=self.envelope_settings,
            nonce_seen=self._nonce_seen,
        )
        if not res.ok:
            self._emit(
                function_id=int(getattr(fx, "function_id", 0) or 0),
                topic=str(getattr(fx, "topic_set", "") or ""),
                value=_extract_text_any(payload),
                ok=False,
                error=str(res.error or "invalid envelope"),
            )
            raise ValueError(str(res.error or "invalid envelope"))

        return res.value

    def handle_ha_set(
        self,
        installation_id: int,
        function_id: int,
        payload: bytes,
        *,
        subkey: str | None = None,
    ) -> None:
        """Handle HA command topics:
        - .../set             (base command)
        - .../<subkey>/set    (extended command channel)
        """
        fx = self.registry.get_function(int(function_id))
        if fx is None:
            self._emit(
                function_id=int(function_id),
                topic="",
                value=None,
                ok=False,
                error="unknown function_id",
            )
            return

        fx_iid = int(getattr(fx, "installation_id", 0) or 0)
        if fx_iid and fx_iid != int(installation_id):
            self._emit(
                function_id=int(function_id),
                topic=getattr(fx, "topic_set", "") or "",
                value=None,
                ok=False,
                error="installation_id mismatch",
            )
            return

        if not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=None, ok=False, error="no topic_set"
            )
            return

        sem = infer_semantics(fx)

        try:
            cmd_value: Any = self._unwrap_if_needed(payload, fx=fx)
        except Exception:
            return

        # ---- SWITCH ----
        if sem.component == "switch":
            on = _extract_bool_any(cmd_value)
            if on is None:
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=_extract_text_any(cmd_value),
                    ok=False,
                    error="invalid bool",
                )
                return
            self.send_switch(int(function_id), on=bool(on))
            return

        # ---- LIGHT ----
        if sem.component == "light":
            if subkey in (None, "state"):
                on = _extract_bool_any(cmd_value)
                if on is None:
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=_extract_text_any(cmd_value),
                        ok=False,
                        error="invalid bool",
                    )
                    return
                self.send_light(int(function_id), on=bool(on))
                return

            if subkey == "brightness":
                bri = _extract_int_any(cmd_value)
                if bri is None:
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=_extract_text_any(cmd_value),
                        ok=False,
                        error="invalid brightness",
                    )
                    return
                self.send_light_brightness(int(function_id), brightness=int(bri))
                return

            if subkey == "color_temp":
                ct = _extract_int_any(cmd_value)
                if ct is None:
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=_extract_text_any(cmd_value),
                        ok=False,
                        error="invalid color_temp",
                    )
                    return
                self.send_light_color_temp(int(function_id), color_temp=int(ct))
                return

            self._emit(
                function_id=int(function_id),
                topic=str(fx.topic_set),
                value=subkey,
                ok=False,
                error="unsupported light subkey",
            )
            return

        # ---- COVER ----
        if sem.component == "cover":
            if subkey in (None, "command"):
                cmd = _extract_text_any(cmd_value).upper()
                if cmd not in ("OPEN", "CLOSE", "STOP"):
                    if isinstance(cmd_value, dict):
                        cmd2 = _extract_text_any(cmd_value.get("command")).upper()
                        if cmd2 in ("OPEN", "CLOSE", "STOP"):
                            cmd = cmd2
                        else:
                            self._emit(
                                function_id=int(function_id),
                                topic=str(fx.topic_set),
                                value=_extract_text_any(cmd_value),
                                ok=False,
                                error="invalid cover cmd",
                            )
                            return
                    else:
                        self._emit(
                            function_id=int(function_id),
                            topic=str(fx.topic_set),
                            value=cmd,
                            ok=False,
                            error="invalid cover cmd",
                        )
                        return
                self.send_cover_command(int(function_id), cmd)
                return

            if subkey == "position":
                pos = _extract_int_any(cmd_value)
                if pos is None:
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=_extract_text_any(cmd_value),
                        ok=False,
                        error="invalid position",
                    )
                    return
                self.send_cover_position(int(function_id), int(pos))
                return

            self._emit(
                function_id=int(function_id),
                topic=str(fx.topic_set),
                value=subkey,
                ok=False,
                error="unsupported cover subkey",
            )
            return

        # ---- CLIMATE ----
        if sem.component == "climate":
            if subkey == "mode":
                mode = _extract_text_any(cmd_value)
                if not mode:
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=mode,
                        ok=False,
                        error="empty mode",
                    )
                    return
                self.send_climate_mode(int(function_id), mode)
                return

            if subkey == "temperature":
                temp = _extract_float_any(cmd_value)
                if temp is None:
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=_extract_text_any(cmd_value),
                        ok=False,
                        error="invalid temperature",
                    )
                    return
                self.send_climate_temperature(int(function_id), float(temp))
                return

            self._emit(
                function_id=int(function_id),
                topic=str(fx.topic_set),
                value=subkey,
                ok=False,
                error="unsupported climate subkey",
            )
            return

        # ---- NUMBER ----
        if sem.component == "number":
            if subkey not in (None, "value"):
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=subkey,
                    ok=False,
                    error="unsupported number subkey",
                )
                return
            val = _extract_float_any(cmd_value)
            if val is None:
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=_extract_text_any(cmd_value),
                    ok=False,
                    error="invalid number",
                )
                return
            self.send_number(int(function_id), float(val))
            return

        # ---- SELECT ----
        if sem.component == "select":
            if subkey not in (None, "option"):
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=subkey,
                    ok=False,
                    error="unsupported select subkey",
                )
                return
            opt = _extract_text_any(cmd_value)
            if not opt:
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=opt,
                    ok=False,
                    error="empty option",
                )
                return
            self.send_select(int(function_id), opt)
            return

        # ---- BUTTON ----
        if sem.component == "button":
            self.press_button(int(function_id))
            return

        self._emit(
            function_id=int(function_id),
            topic=str(fx.topic_set),
            value=subkey,
            ok=False,
            error=f"unsupported component {sem.component}",
        )

    # ---------- publish helpers ----------

    def _publish(self, fx: FunctionX, value: Any) -> bool:
        topic = str(fx.topic_set)

        try:
            self.policy.require_publish(topic)
        except PolicyDenied as e:
            self._emit(
                function_id=int(fx.function_id), topic=topic, value=value, ok=False, error=str(e)
            )
            return False

        # Lynx upstream expects ValueMessage on /set topics.
        try:
            if _is_set_topic(topic):
                payload: Any = _lynx_value_message(value)
            elif _is_cmd_topic(topic):
                # For cmd topics an empty object is typically sufficient.
                payload = {} if value is None else value
            else:
                payload = value
        except Exception as e:
            self._emit(
                function_id=int(fx.function_id), topic=topic, value=value, ok=False, error=str(e)
            )
            return False

        try:
            self.mqtt_publish(topic, _encode_payload(payload), _QOS, _RETAIN)
        except Exception as e:
            _LOGGER.debug("Publish failed function_id=%s topic=%s err=%s", fx.function_id, topic, e)
            self._emit(
                function_id=int(fx.function_id), topic=topic, value=value, ok=False, error=str(e)
            )
            return False

        self._emit(function_id=int(fx.function_id), topic=topic, value=value, ok=True)
        return True

    def send_switch(self, function_id: int, on: bool) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=on, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, _switch_publish_value(fx, on))

    def send_light(self, function_id: int, on: bool) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=on, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, _switch_publish_value(fx, on))

    def send_light_brightness(self, function_id: int, brightness: int) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value=brightness,
                ok=False,
                error="no topic_set",
            )
            return
        self._publish(fx, int(brightness))

    def send_light_color_temp(self, function_id: int, color_temp: int) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value=color_temp,
                ok=False,
                error="no topic_set",
            )
            return
        self._publish(fx, int(color_temp))

    def send_cover_command(self, function_id: int, cmd: str) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=cmd, ok=False, error="no topic_set"
            )
            return
        # Cover commands are frequently implemented as /cmd topics; if it's /set, this will be rejected (by design).
        self._publish(fx, {"command": str(cmd)} if _is_cmd_topic(str(fx.topic_set)) else cmd)

    def send_cover_position(self, function_id: int, position: int) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value=position,
                ok=False,
                error="no topic_set",
            )
            return
        self._publish(fx, int(position))

    def send_climate_mode(self, function_id: int, mode: str) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=mode, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, {"mode": str(mode)} if _is_cmd_topic(str(fx.topic_set)) else mode)

    def send_climate_temperature(self, function_id: int, temperature: float) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value=temperature,
                ok=False,
                error="no topic_set",
            )
            return
        self._publish(fx, float(temperature))

    def send_number(self, function_id: int, value: float) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=value, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, float(value))

    def send_select(self, function_id: int, option: str) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=option, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, {"option": str(option)} if _is_cmd_topic(str(fx.topic_set)) else option)

    def press_button(self, function_id: int) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value="PRESS",
                ok=False,
                error="no topic_set",
            )
            return
        # Prefer cmd topics; for set topics we send value=1.
        if _is_cmd_topic(str(fx.topic_set)):
            self._publish(fx, {})
        else:
            self._publish(fx, 1)
