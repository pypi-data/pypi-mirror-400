# File: src/iotopen_bridge/security/policy_engine.py
# SPDX-License-Identifier: Apache-2.0

"""
Compatibility shim (deprecated).

Use iotopen_bridge.security.guardrails instead.
"""

from __future__ import annotations

from .guardrails import GuardDecision as PolicyDecision
from .guardrails import Guardrails as PolicyEngine
from .guardrails import GuardrailsConfig as PolicyConfig

__all__ = ["PolicyConfig", "PolicyDecision", "PolicyEngine"]
