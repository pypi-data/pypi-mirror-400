# File: src/iotopen_bridge/controllers/scheduler.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
import random
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class PeriodicTask:
    """Simple periodic scheduler.

    Enhancements over minimal version:
      - jitter support (uniform +/- jitter_sec)
      - drift-corrected scheduling (doesn't accumulate delay)
      - exception isolation (task failures don't kill loop)
      - optional name for thread/debugging
    """

    interval_sec: float
    fn: Callable[[], None]
    jitter_sec: float = 0.0
    name: str = "periodic-task"

    def start(self, stop_event: threading.Event) -> None:
        interval = max(0.01, float(self.interval_sec))
        jitter = max(0.0, float(self.jitter_sec))

        next_run = time.monotonic()

        while not stop_event.is_set():
            now = time.monotonic()
            if now < next_run:
                time.sleep(min(0.5, next_run - now))
                continue

            # Run
            # isolate failure; rely on app logging elsewhere
            with contextlib.suppress(Exception):
                self.fn()

            # Schedule next run (drift-corrected)
            next_run += interval
            if jitter:
                next_run += random.uniform(-jitter, jitter)

            # If we fell behind badly, resync
            if (time.monotonic() - next_run) > (interval * 5):
                next_run = time.monotonic() + interval

    def start_in_thread(
        self, stop_event: threading.Event, *, daemon: bool = True
    ) -> threading.Thread:
        t = threading.Thread(target=self.start, args=(stop_event,), name=self.name, daemon=daemon)
        t.start()
        return t
