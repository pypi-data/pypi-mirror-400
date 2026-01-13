# File: src/iotopen_bridge/core/event_bus.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

_LOGGER = logging.getLogger(__name__)
T = TypeVar("T")


@dataclass(frozen=True)
class Subscription:
    event_type: type[Any]
    handler_id: int


class EventBus:
    """Thread-safe, synchronous event bus.

    Design goals:
      - Zero dependencies
      - Safe from handler exceptions (one handler can't kill the bus)
      - Fast: O(#handlers for type) dispatch
      - Optional wildcard handlers (subscribe to object)
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._next_id = 1
        self._handlers: dict[type[Any], dict[int, Callable[[Any], None]]] = {}

    def subscribe(self, event_type: type[T], handler: Callable[[T], None]) -> Subscription:
        with self._lock:
            hid = self._next_id
            self._next_id += 1
            m = self._handlers.setdefault(event_type, {})
            m[hid] = handler  # type: ignore[assignment]
            return Subscription(event_type=event_type, handler_id=hid)

    def unsubscribe(self, sub: Subscription) -> None:
        with self._lock:
            m = self._handlers.get(sub.event_type)
            if not m:
                return
            m.pop(sub.handler_id, None)
            if not m:
                self._handlers.pop(sub.event_type, None)

    def publish(self, event: Any) -> None:
        et = type(event)

        # Snapshot handlers outside call path for safety
        with self._lock:
            exact = list(self._handlers.get(et, {}).values())
            wild = list(self._handlers.get(object, {}).values())

        # Dispatch exact then wildcard
        for h in exact:
            try:
                h(event)
            except Exception as e:
                _LOGGER.debug("Event handler error (%s): %s", et.__name__, e)

        for h in wild:
            try:
                h(event)
            except Exception as e:
                _LOGGER.debug("Wildcard event handler error (%s): %s", et.__name__, e)
