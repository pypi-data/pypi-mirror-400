# File: src/iotopen_bridge/transport/mqtt/null_client.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass

from .base import ConnectHandler, MessageHandler

DisconnectHandler = ConnectHandler


@dataclass
class NullMqttClient:
    """A no-op MQTT client used when HA transport is disabled.

    The bridge runtime is written around an MQTT client interface; using this lets
    us keep those code paths simple while running without a downstream broker.
    """

    _on_message: MessageHandler | None = None
    _on_connect: ConnectHandler | None = None
    _on_disconnect: DisconnectHandler | None = None

    @property
    def is_connected(self) -> bool:
        return False

    def set_on_message(self, handler: MessageHandler) -> None:
        self._on_message = handler

    def set_on_connect(self, handler: ConnectHandler) -> None:
        self._on_connect = handler

    def set_on_disconnect(self, handler: DisconnectHandler) -> None:
        self._on_disconnect = handler

    def connect(self) -> None:
        # Immediately report "connected" (as ok=False) to keep logs consistent.
        if self._on_connect:
            self._on_connect(False, "disabled")

    def disconnect(self) -> None:
        if self._on_disconnect:
            self._on_disconnect(True, "disabled")

    def subscribe(self, topic: str, qos: int = 0) -> None:
        return

    def unsubscribe(self, topic: str) -> None:
        return

    def publish(self, topic: str, payload: str | bytes, qos: int = 0, retain: bool = False) -> None:
        return
