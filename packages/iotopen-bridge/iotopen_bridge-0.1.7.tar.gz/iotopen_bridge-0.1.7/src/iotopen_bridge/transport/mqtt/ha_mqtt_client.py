from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ...adapters.raw_capture import RawCapture

MessageHandler = Callable[[str, bytes, int, bool], None]
ConnectHandler = Callable[[bool, str], None]


@dataclass(frozen=True)
class HaMqttConfig:
    client_id: str = "iotopen-bridge"


class HaMqttClient:
    """
    IMqttClient adapter that uses Home Assistant's MQTT integration.
    Embedded mode only.
    """

    def __init__(
        self, hass: Any, cfg: HaMqttConfig | None = None, *, raw_capture: RawCapture | None = None
    ) -> None:
        self.hass = hass
        self.cfg = cfg or HaMqttConfig()
        self._raw_capture = raw_capture

        self._on_msg: MessageHandler | None = None
        self._on_conn: ConnectHandler | None = None

        self._unsubs: dict[str, Callable[[], None]] = {}
        self._tasks: set[asyncio.Task[Any]] = set()

    def set_on_message(self, handler: MessageHandler) -> None:
        self._on_msg = handler

    def set_on_connect(self, handler: ConnectHandler) -> None:
        self._on_conn = handler

    def connect(self) -> None:
        if self._on_conn:
            self._on_conn(True, "embedded")

    def disconnect(self) -> None:
        for topic in list(self._unsubs.keys()):
            with contextlib.suppress(Exception):
                self.unsubscribe(topic)
        if self._on_conn:
            self._on_conn(False, "embedded-disconnect")

    def subscribe(self, topic: str, qos: int = 0) -> None:
        self._schedule(self._async_subscribe(topic, qos))

    def unsubscribe(self, topic: str) -> None:
        unsub = self._unsubs.pop(topic, None)
        if unsub is not None:
            with contextlib.suppress(Exception):
                unsub()

    def publish(self, topic: str, payload: str | bytes, qos: int = 0, retain: bool = False) -> None:
        payload_bytes = payload if isinstance(payload, bytes) else payload.encode("utf-8")

        if self._raw_capture:
            with contextlib.suppress(Exception):
                self._raw_capture.capture_mqtt_message(
                    "tx",
                    topic=topic,
                    payload=payload_bytes,
                    qos=int(qos),
                    retain=bool(retain),
                    meta={"client_id": self.cfg.client_id, "embedded": True},
                )

        self._schedule(self._async_publish(topic, payload, qos, retain))

    # ---- internals ----

    def _schedule(self, coro) -> None:
        loop = self.hass.loop
        if loop.is_running():
            try:
                running = asyncio.get_running_loop()
            except RuntimeError:
                running = None

            if running is loop:
                task = asyncio.create_task(coro)
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)
            else:
                asyncio.run_coroutine_threadsafe(coro, loop)
        else:  # pragma: no cover
            loop.run_until_complete(coro)

    async def _async_publish(
        self, topic: str, payload: str | bytes, qos: int, retain: bool
    ) -> None:
        ha_mqtt = self._import_ha_mqtt()
        await ha_mqtt.async_publish(self.hass, topic, payload, qos=qos, retain=retain)

    async def _async_subscribe(self, topic: str, qos: int) -> None:
        ha_mqtt = self._import_ha_mqtt()

        old = self._unsubs.pop(topic, None)
        if old is not None:
            with contextlib.suppress(Exception):
                old()

        async def _cb(msg: Any) -> None:
            t = str(getattr(msg, "topic", ""))
            p = getattr(msg, "payload", b"")
            q = int(getattr(msg, "qos", 0))
            r = bool(getattr(msg, "retain", False))

            payload_bytes = p if isinstance(p, bytes) else str(p).encode("utf-8")

            if self._raw_capture:
                with contextlib.suppress(Exception):
                    self._raw_capture.capture_mqtt_message(
                        "rx",
                        topic=t,
                        payload=payload_bytes,
                        qos=q,
                        retain=r,
                        meta={"client_id": self.cfg.client_id, "embedded": True},
                    )

            if self._on_msg:
                self._on_msg(t, payload_bytes, q, r)

        unsub = await ha_mqtt.async_subscribe(self.hass, topic, _cb, qos=qos, encoding=None)
        self._unsubs[topic] = unsub

    @staticmethod
    def _import_ha_mqtt():
        try:
            from homeassistant.components import mqtt as ha_mqtt  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "Home Assistant mqtt integration is required for HaMqttClient"
            ) from e
        return ha_mqtt
