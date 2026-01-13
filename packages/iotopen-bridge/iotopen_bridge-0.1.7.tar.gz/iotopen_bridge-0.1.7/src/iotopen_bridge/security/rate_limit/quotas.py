from dataclasses import dataclass


@dataclass(frozen=True)
class Quotas:
    messages_per_sec: float = 20.0
    burst: float = 50.0
