# File: src/iotopen_bridge/adapters/ha_native_publisher.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class NativeStateSnapshot:
    """Immutable read model for a single function."""

    installation_id: int
    function_id: int
    available: bool
    last_seen: float | None
    state: bytes | None
    attributes: dict[str, Any] | None


class NativeStateStore:
    """Thread-safe in-memory HA state store.

    This replaces MQTT state topics when ha.transport="native".

    Notes
    -----
    - We store raw bytes for state so callers can choose decoding (bool/int/json/etc).
    - Attributes are stored as a dict and should remain JSON-serializable.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._state: dict[tuple[int, int], bytes] = {}
        self._attrs: dict[tuple[int, int], dict[str, Any]] = {}
        self._avail: dict[tuple[int, int], bool] = {}
        self._seen: dict[tuple[int, int], float] = {}

    def set_available(self, installation_id: int, function_id: int, available: bool) -> None:
        key = (int(installation_id), int(function_id))
        with self._lock:
            self._avail[key] = bool(available)
            self._seen[key] = time.time()

    def set_state(self, installation_id: int, function_id: int, payload: bytes) -> None:
        key = (int(installation_id), int(function_id))
        with self._lock:
            self._state[key] = bytes(payload)
            # In native mode, receiving state implies the entity is alive.
            # Mark available=True unless an explicit availability message says otherwise.
            self._avail.setdefault(key, True)
            self._seen[key] = time.time()

    def set_attributes(self, installation_id: int, function_id: int, attrs: dict[str, Any]) -> None:
        key = (int(installation_id), int(function_id))
        with self._lock:
            self._attrs[key] = dict(attrs)
            self._avail.setdefault(key, True)
            self._seen[key] = time.time()

    def get_snapshot(self, installation_id: int, function_id: int) -> NativeStateSnapshot:
        key = (int(installation_id), int(function_id))
        with self._lock:
            return NativeStateSnapshot(
                installation_id=key[0],
                function_id=key[1],
                # Default to available=True so entities are usable immediately in native mode.
                available=bool(self._avail.get(key, True)),
                last_seen=self._seen.get(key),
                state=self._state.get(key),
                attributes=dict(self._attrs[key]) if key in self._attrs else None,
            )

    # Backwards-compatible alias used by the HA integration.
    def snapshot(self, installation_id: int, function_id: int) -> NativeStateSnapshot:
        return self.get_snapshot(installation_id, function_id)

    def drop_function(self, installation_id: int, function_id: int) -> None:
        key = (int(installation_id), int(function_id))
        with self._lock:
            self._state.pop(key, None)
            self._attrs.pop(key, None)
            self._avail.pop(key, None)
            self._seen.pop(key, None)


@dataclass
class HANativePublisher:
    """Drop-in replacement for HADiscoveryPublisher used by TelemetryController.

    Only the methods actually used by TelemetryController / availability watchdog are implemented.
    """

    state_prefix: str
    attributes_enabled: bool
    per_entity_availability: bool
    store: NativeStateStore

    # The MQTT version has these, so keep for compatibility.
    discovery_prefix: str = ""
    bridge_availability_topic: str = ""

    # --- no-op discovery interface (keeps runtime code paths simple) ---
    def publish_all(self) -> int:  # pragma: no cover
        return 0

    def garbage_collect(self, removed_functions) -> int:  # pragma: no cover
        # The HA integration is responsible for removing entities.
        return 0

    def publish_bridge_availability(
        self, online: bool, *, qos: int = 1, retain: bool = True
    ) -> None:
        # HA integration can expose bridge status separately.
        return

    # --- state/attributes paths ---
    def publish_entity_availability(
        self, installation_id: int, function_id: int, online: bool
    ) -> None:
        if not self.per_entity_availability:
            return
        self.store.set_available(int(installation_id), int(function_id), bool(online))

    def publish_attributes(
        self,
        installation_id: int,
        function_id: int,
        attrs: dict[str, Any],
        qos: int,
        retain: bool,
    ) -> None:
        if not self.attributes_enabled:
            return
        self.store.set_attributes(int(installation_id), int(function_id), dict(attrs))

    def publish(self, topic: str, payload: str | bytes, qos: int, retain: bool) -> None:
        # TelemetryController publishes: {state_prefix}/{iid}/{fid}/state (and some subkeys)
        # We only store base state; subkey state is exposed via attributes anyway.
        try:
            parts = str(topic or "").strip("/").split("/")
            # Expected: <prefix>/<iid>/<fid>/state
            if len(parts) < 4:
                return
            prefix, iid_s, fid_s, key = parts[0], parts[1], parts[2], parts[3]
            if prefix != str(self.state_prefix).strip("/"):
                return
            if key != "state":
                return
            iid = int(iid_s)
            fid = int(fid_s)
        except Exception:
            return

        b = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
        self.store.set_state(iid, fid, b)
