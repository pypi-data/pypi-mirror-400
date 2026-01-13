# File: src/iotopen_bridge/core/backoff.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Backoff:
    base: float = 1.0
    cap: float = 30.0
    factor: float = 2.0
    _cur: float = 0.0

    def next(self) -> float:
        self._cur = self.base if self._cur == 0.0 else min(self.cap, self._cur * self.factor)
        return self._cur

    def reset(self) -> None:
        self._cur = 0.0
