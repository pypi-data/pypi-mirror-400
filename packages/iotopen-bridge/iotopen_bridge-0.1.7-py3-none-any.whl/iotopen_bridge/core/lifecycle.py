# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/core/lifecycle.py

"""Lifecycle helpers.

- Protocols (Startable/Stoppable) are used by runtime orchestration.
- Lifecycle is an optional coordinator for start/stop hook ordering.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from .errors import LifecycleError

_LOGGER = logging.getLogger(__name__)


class Startable(Protocol):
    def start(self) -> None: ...


class Stoppable(Protocol):
    def stop(self) -> None: ...


Hook = Callable[[], None]


@dataclass(slots=True)
class LifecycleHooks:
    on_start: list[Hook]
    on_stop: list[Hook]

    def __init__(self) -> None:
        self.on_start = []
        self.on_stop = []


class Lifecycle:
    """Idempotent start/stop coordinator."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._started = False
        self.hooks = LifecycleHooks()

    @property
    def started(self) -> bool:
        with self._lock:
            return self._started

    def add_start_hook(self, hook: Hook) -> None:
        with self._lock:
            self.hooks.on_start.append(hook)

    def add_stop_hook(self, hook: Hook) -> None:
        with self._lock:
            self.hooks.on_stop.append(hook)

    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            self._started = True
            hooks = list(self.hooks.on_start)
        for h in hooks:
            try:
                h()
            except Exception:
                _LOGGER.exception("Lifecycle start hook crashed (ignored). hook=%r", h)

    def stop(self) -> None:
        with self._lock:
            if not self._started:
                return
            self._started = False
            hooks = list(reversed(self.hooks.on_stop))
        for h in hooks:
            try:
                h()
            except Exception:
                _LOGGER.exception("Lifecycle stop hook crashed (ignored). hook=%r", h)

    def require_started(self) -> None:
        if not self.started:
            raise LifecycleError("Component has not been started")
