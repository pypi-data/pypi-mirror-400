# File: src/iotopen_bridge/core/clock.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol


class Clock(Protocol):
    def now(self) -> float: ...


@dataclass(frozen=True)
class SystemClock:
    """Real wall-clock time (epoch seconds)."""

    def now(self) -> float:
        return time.time()


@dataclass(frozen=True)
class MonotonicClock:
    """Monotonic time (seconds) for scheduling/backoff (not epoch)."""

    def now(self) -> float:
        return time.monotonic()
