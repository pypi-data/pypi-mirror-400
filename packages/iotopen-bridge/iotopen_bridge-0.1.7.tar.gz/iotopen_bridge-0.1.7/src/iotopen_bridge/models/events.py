# File: src/iotopen_bridge/models/events.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class BaseEvent:
    """Base class for events published on the internal EventBus.

    Conventions:
      - timestamp is unix seconds
      - events are immutable (frozen)
      - keep payloads JSON-serializable when possible
    """

    timestamp: float = field(default_factory=lambda: time.time())

    @property
    def event_type(self) -> str:
        return self.__class__.__name__


# ----------------------------
# Inventory / discovery events
# ----------------------------


@dataclass(frozen=True, slots=True)
class InventoryEvent(BaseEvent):
    """Emitted after an inventory refresh + registry apply."""

    changed: bool = False
    function_count: int = 0

    # Keep removed_functions as dicts because GC/publisher expects dict-like fields.
    removed_functions: Sequence[dict[str, Any]] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class DiscoveryEvent(BaseEvent):
    """Emitted when discovery publish/GC occurs (optional)."""

    published: int = 0
    garbage_collected: int = 0


# ----------------------------
# Telemetry / command events
# ----------------------------


@dataclass(frozen=True, slots=True)
class TelemetryEvent(BaseEvent):
    """Emitted for inbound telemetry messages (optional; can be high-volume)."""

    topic: str = ""
    installation_id: int = 0
    function_id: int = 0
    qos: int = 0
    retain: bool = False
    payload: bytes = b""


@dataclass(frozen=True, slots=True)
class CommandEvent(BaseEvent):
    """Emitted when a command is accepted/blocked/published."""

    function_id: int = 0
    topic: str = ""
    value: Any = None
    ok: bool = False
    error: str | None = None
