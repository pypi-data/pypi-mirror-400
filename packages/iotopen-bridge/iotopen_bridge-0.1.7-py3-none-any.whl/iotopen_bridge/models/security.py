# File: src/iotopen_bridge/models/security.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AuditLevel(str, Enum):
    """Audit severity level (string enum for easy JSON)."""

    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Structured audit event (JSON-friendly)."""

    level: AuditLevel
    action: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"level": self.level.value, "action": self.action, "data": dict(self.data)}
