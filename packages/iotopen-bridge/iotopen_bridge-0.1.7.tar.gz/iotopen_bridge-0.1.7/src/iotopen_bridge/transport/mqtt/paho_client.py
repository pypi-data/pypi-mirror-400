# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/transport/mqtt/paho_client.py
from __future__ import annotations

import contextlib
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import paho.mqtt.client as mqtt

from ...adapters.raw_capture import RawCapture
from ...core.errors import PolicyDenied
from ...security.authz.policy import PolicyEngine
from ...security.tls.context import build_ssl_context
from ...security.tls.profiles import TLSSettings

_LOGGER = logging.getLogger(__name__)

MessageHandler = Callable[[str, bytes, int, bool], None]
ConnectHandler = Callable[[bool, str], None]
DisconnectHandler = Callable[[int, str], None]


def _rc_to_int(rc: Any) -> int:
    if rc is None:
        return 0
    with contextlib.suppress(Exception):
        v = getattr(rc, "value", None)
        if v is not None:
            return int(v)
    try:
        return int(rc)
    except Exception:
        return 0


def _make_client(cfg_client_id: str) -> mqtt.Client:
    try:
        capi = getattr(mqtt, "CallbackAPIVersion", None)
        if capi is not None and hasattr(capi, "VERSION2"):
            return mqtt.Client(
                callback_api_version=capi.VERSION2,
                client_id=cfg_client_id,
                protocol=mqtt.MQTTv311,
            )
    except TypeError:
        pass
    except Exception:
        pass

    return mqtt.Client(client_id=cfg_client_id, protocol=mqtt.MQTTv311)


@dataclass(frozen=True)
class PahoMqttConfig:
    host: str
    port: int = 1883
    username: str | None = None
    password: str | None = None
    client_id: str = "iotopen-bridge"
    keepalive: int = 60

    tls: TLSSettings = field(default_factory=TLSSettings)

    will_topic: str | None = None
    will_payload: str | bytes | None = None
    will_qos: int = 0
    will_retain: bool = True

    # resilience knobs
    reconnect_min_delay: int = 1
    reconnect_max_delay: int = 60
    enable_paho_logger: bool = True


class PahoMqttClient:
    def __init__(
        self,
        cfg: PahoMqttConfig,
        *,
        raw_capture: RawCapture,
        policy: PolicyEngine | None = None,
    ) -> None:
        self.cfg = cfg
        self.raw_capture = raw_capture
        self.policy = policy

        self._client = _make_client(cfg.client_id)

        self._on_message: MessageHandler | None = None
        self._on_connect: ConnectHandler | None = None
        self._on_disconnect: DisconnectHandler | None = None

        self._connected = threading.Event()
        self._lock = threading.RLock()

        self._subscriptions: dict[str, int] = {}

        # Route paho logs into our logger
        if bool(cfg.enable_paho_logger):
            with contextlib.suppress(Exception):
                self._client.enable_logger(_LOGGER)

        # Backoff reconnect storms
        with contextlib.suppress(Exception):
            self._client.reconnect_delay_set(
                min_delay=int(cfg.reconnect_min_delay),
                max_delay=int(cfg.reconnect_max_delay),
            )

        if cfg.username is not None:
            self._client.username_pw_set(cfg.username, cfg.password)

        tls = TLSSettings.from_any(cfg.tls)
        if tls.enabled:
            ctx = build_ssl_context(tls)
            self._client.tls_set_context(ctx)
            if tls.insecure:
                # NOTE: intentionally explicit + opt-in; config should make this loud.
                self._client.tls_insecure_set(True)

        if cfg.will_topic:
            self._client.will_set(
                topic=str(cfg.will_topic),
                payload=cfg.will_payload,
                qos=int(cfg.will_qos),
                retain=bool(cfg.will_retain),
            )

        self._client.on_connect = self._handle_connect
        self._client.on_disconnect = self._handle_disconnect
        self._client.on_message = self._handle_message

    @property
    def is_connected(self) -> bool:
        return bool(self._connected.is_set())

    def set_on_message(self, handler: MessageHandler) -> None:
        self._on_message = handler

    def set_on_connect(self, handler: ConnectHandler) -> None:
        self._on_connect = handler

    def set_on_disconnect(self, handler: DisconnectHandler) -> None:
        self._on_disconnect = handler

    def connect(self) -> None:
        with self._lock:
            self._client.connect(self.cfg.host, int(self.cfg.port), int(self.cfg.keepalive))
            self._client.loop_start()

    def disconnect(self) -> None:
        with self._lock:
            try:
                self._client.disconnect()
            finally:
                try:
                    self._client.loop_stop()
                except TypeError:
                    with contextlib.suppress(Exception):
                        self._client.loop_stop()
                except Exception:
                    pass
            self._connected.clear()

    def wait_connected(self, timeout: float = 10.0) -> bool:
        return bool(self._connected.wait(timeout=float(timeout)))

    def subscribe(self, topic_filter: str, qos: int = 0) -> None:
        topic_s = str(topic_filter)
        if self.policy is not None:
            try:
                self.policy.require_subscribe(topic_s)
            except PolicyDenied as e:
                _LOGGER.warning("AUTHZ denied subscribe: %s", e)
                return

        with self._lock:
            self._subscriptions[topic_s] = int(qos)
            self._client.subscribe(topic_s, qos=int(qos))

    def unsubscribe(self, topic_filter: str) -> None:
        topic_s = str(topic_filter)
        with self._lock:
            self._subscriptions.pop(topic_s, None)
            self._client.unsubscribe(topic_s)

    def publish(self, topic: str, payload: str | bytes, qos: int = 0, retain: bool = False) -> None:
        topic_s = str(topic)
        if self.policy is not None:
            try:
                self.policy.require_publish(topic_s)
            except PolicyDenied as e:
                _LOGGER.warning("AUTHZ denied publish: %s", e)
                return

        b = payload if isinstance(payload, (bytes, bytearray)) else str(payload).encode("utf-8")

        with contextlib.suppress(Exception):
            self.raw_capture.capture_tx(topic_s, bytes(b), int(qos), bool(retain))

        self._client.publish(topic_s, bytes(b), qos=int(qos), retain=bool(retain))

    def _handle_connect(
        self, _client: Any, _userdata: Any, _flags: Any, rc_or_reason: Any, *args: Any
    ) -> None:
        rc = _rc_to_int(rc_or_reason)
        ok = rc == 0

        if ok:
            self._connected.set()
        else:
            self._connected.clear()

        # Re-subscribe after reconnect
        if ok:
            try:
                with self._lock:
                    items = list(self._subscriptions.items())
                for topic, qos in items:
                    try:
                        self._client.subscribe(topic, qos=int(qos))
                    except Exception:
                        _LOGGER.debug("Resubscribe failed topic=%r", topic, exc_info=True)
            except Exception:
                _LOGGER.debug("Resubscribe sweep failed", exc_info=True)

        if self._on_connect:
            with contextlib.suppress(Exception):
                self._on_connect(ok, f"rc={rc}")

    def _handle_disconnect(
        self, _client: Any, _userdata: Any, rc_or_reason: Any, *args: Any
    ) -> None:
        self._connected.clear()
        rc = _rc_to_int(rc_or_reason)

        # Tests expect *exactly* "rc=<n>" (no prefixes like "unexpected"/"clean")
        msg = f"rc={rc}"

        if self._on_disconnect:
            with contextlib.suppress(Exception):
                self._on_disconnect(rc, msg)

        # backwards compat: also signal connect callback
        if self._on_connect:
            with contextlib.suppress(Exception):
                self._on_connect(False, msg)

    def _handle_message(self, _client: Any, _userdata: Any, msg: Any) -> None:
        topic = str(getattr(msg, "topic", ""))
        payload: bytes = bytes(getattr(msg, "payload", b""))
        qos = int(getattr(msg, "qos", 0))
        retain = bool(getattr(msg, "retain", False))

        with contextlib.suppress(Exception):
            self.raw_capture.capture_rx(topic, payload, qos, retain)

        if self._on_message:
            with contextlib.suppress(Exception):
                self._on_message(topic, payload, qos, retain)
