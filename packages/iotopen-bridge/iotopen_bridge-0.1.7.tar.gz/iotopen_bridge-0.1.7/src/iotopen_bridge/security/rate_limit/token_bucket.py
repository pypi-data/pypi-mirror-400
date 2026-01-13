import time
from dataclasses import dataclass


@dataclass
class TokenBucket:
    rate_per_sec: float
    capacity: float
    tokens: float = 0.0
    last_ts: float = 0.0

    def allow(self, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        if self.last_ts == 0.0:
            self.last_ts = now
            self.tokens = self.capacity
        dt = max(0.0, now - self.last_ts)
        self.last_ts = now
        self.tokens = min(self.capacity, self.tokens + dt * self.rate_per_sec)
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False
