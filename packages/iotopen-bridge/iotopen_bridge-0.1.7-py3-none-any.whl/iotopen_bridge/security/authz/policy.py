# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/authz/policy.py
from __future__ import annotations

import enum
import logging
from dataclasses import dataclass
from typing import Any

from ...core.errors import PolicyDenied
from .rules import AuthzRules

_LOGGER = logging.getLogger(__name__)


class PolicyMode(str, enum.Enum):
    DISABLED = "disabled"
    MONITOR = "monitor"
    ENFORCE = "enforce"


def _norm_mode(mode: Any) -> PolicyMode:
    if isinstance(mode, PolicyMode):
        return mode
    s = str(mode or "").strip().lower()
    if s in ("", "disabled", "off", "false", "0"):
        return PolicyMode.DISABLED
    if s in ("monitor", "observe", "audit", "log"):
        return PolicyMode.MONITOR
    return PolicyMode.ENFORCE


@dataclass
class PolicyEngine:
    """Thin wrapper around AuthzRules with an operator mode (disabled/monitor/enforce)."""

    rules: AuthzRules
    mode: PolicyMode = PolicyMode.ENFORCE

    def __init__(self, rules: AuthzRules, mode: Any = PolicyMode.ENFORCE) -> None:
        self.rules = rules
        self.mode = _norm_mode(mode)

    def require_publish(self, topic: str) -> None:
        if self.mode == PolicyMode.DISABLED:
            return
        try:
            self.rules.require_publish(topic)
        except PolicyDenied:
            if self.mode == PolicyMode.MONITOR:
                _LOGGER.warning("AUTHZ monitor: would deny publish topic=%r", topic)
                return
            raise

    def require_subscribe(self, topic_filter: str) -> None:
        if self.mode == PolicyMode.DISABLED:
            return
        try:
            self.rules.require_subscribe(topic_filter)
        except PolicyDenied:
            if self.mode == PolicyMode.MONITOR:
                _LOGGER.warning("AUTHZ monitor: would deny subscribe filter=%r", topic_filter)
                return
            raise
