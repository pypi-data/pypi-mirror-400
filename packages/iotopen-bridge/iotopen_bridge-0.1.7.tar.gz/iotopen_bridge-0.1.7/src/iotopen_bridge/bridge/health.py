# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/bridge/health.py
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Health:
    """In-proc health model (tiny + dependency-free).

    Intended usage:
      - bridge.runtime updates this from MQTT/inventory threads
      - bridge.health_http reads snapshots for /healthz and /readyz
    """

    mqtt_connected: bool = False
    last_mqtt_ts: float | None = None

    last_inventory_ok: bool = False
    last_inventory_ts: float | None = None

    last_error: str | None = None
    last_error_ts: float | None = None
    last_error_count: int = 0

    _lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)

    @property
    def ready(self) -> bool:
        """Conservative readiness: requires MQTT connected AND last inventory OK."""
        with self._lock:
            return bool(self.mqtt_connected) and bool(self.last_inventory_ok)

    def set_connected(self, connected: bool, *, timestamp: float | None = None) -> None:
        ts = time.time() if timestamp is None else float(timestamp)
        with self._lock:
            self.mqtt_connected = bool(connected)
            self.last_mqtt_ts = ts

    def set_inventory_ok(self, ok: bool, *, timestamp: float | None = None) -> None:
        ts = time.time() if timestamp is None else float(timestamp)
        with self._lock:
            self.last_inventory_ok = bool(ok)
            self.last_inventory_ts = ts

    def set_error(self, message: str | None, *, timestamp: float | None = None) -> None:
        ts = time.time() if timestamp is None else float(timestamp)
        with self._lock:
            self.last_error = message
            self.last_error_ts = ts
            if message:
                self.last_error_count += 1

    def clear_error(self) -> None:
        with self._lock:
            self.last_error = None
            self.last_error_ts = None

    def snapshot(self) -> dict[str, Any]:
        """Thread-safe snapshot for HTTP endpoints / logs."""
        with self._lock:
            return {
                "mqtt_connected": bool(self.mqtt_connected),
                "last_mqtt_ts": self.last_mqtt_ts,
                "last_inventory_ok": bool(self.last_inventory_ok),
                "last_inventory_ts": self.last_inventory_ts,
                "ready": bool(self.ready),
                "last_error": self.last_error,
                "last_error_ts": self.last_error_ts,
                "last_error_count": int(self.last_error_count),
            }


# Backwards/forwards compat: some code imports BridgeHealth
BridgeHealth = Health

__all__ = ["BridgeHealth", "Health"]
