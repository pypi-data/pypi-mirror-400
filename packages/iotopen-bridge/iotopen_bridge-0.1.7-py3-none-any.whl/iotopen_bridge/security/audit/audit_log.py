# File: src/iotopen_bridge/security/audit/audit_log.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
import time
from dataclasses import dataclass
from typing import Any

from .sinks import AuditSink


@dataclass
class AuditLog:
    """Structured audit log (security + operator-grade)."""

    sinks: list[AuditSink]

    def write(
        self,
        action: str,
        *,
        outcome: str = "ok",
        actor: str = "bridge",
        subject: str | None = None,
        details: dict[str, Any] | None = None,
        severity: str = "info",
    ) -> None:
        rec: dict[str, Any] = {
            "ts": time.time(),
            "action": str(action),
            "outcome": str(outcome),
            "actor": str(actor),
            "severity": str(severity),
        }
        if subject:
            rec["subject"] = str(subject)
        if details:
            rec["details"] = details

        for s in self.sinks:
            with contextlib.suppress(Exception):
                s.emit(rec)
