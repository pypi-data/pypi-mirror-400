# File: src/iotopen_bridge/security/guardrails.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GuardDecision:
    allow: bool
    reason: str


@dataclass(frozen=True)
class GuardrailsConfig:
    allow_commands: bool = True
    allow_insecure_tls: bool = False
    max_payload_bytes: int = 256_000


class Guardrails:
    def __init__(self, cfg: GuardrailsConfig) -> None:
        self.cfg = cfg

    def can_send_command(self) -> GuardDecision:
        if not self.cfg.allow_commands:
            return GuardDecision(False, "commands_disabled")
        return GuardDecision(True, "ok")

    def can_use_insecure_tls(self) -> GuardDecision:
        if self.cfg.allow_insecure_tls:
            return GuardDecision(True, "ok")
        return GuardDecision(False, "insecure_tls_disabled")

    def can_accept_payload(self, nbytes: int) -> GuardDecision:
        if int(nbytes) > int(self.cfg.max_payload_bytes):
            return GuardDecision(False, "payload_too_large")
        return GuardDecision(True, "ok")
