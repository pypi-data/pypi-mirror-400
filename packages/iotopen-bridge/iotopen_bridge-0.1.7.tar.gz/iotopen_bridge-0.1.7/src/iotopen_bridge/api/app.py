# File: src/iotopen_bridge/bridge/app.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass

from ..bridge.config import BridgeConfig
from ..bridge.runtime import BridgeRuntime
from ..observability.metrics import Metrics
from ..security.audit.audit_log import AuditLog
from ..security.audit.sinks import JsonlStdoutSink
from ..security.policy_engine import PolicyConfig, PolicyEngine


@dataclass
class BridgeApp:
    """Thin wrapper to compose runtime + policy + audit.

    Keeping this separate makes Supervisor integration clean.
    """

    cfg: BridgeConfig
    metrics: Metrics

    def __post_init__(self) -> None:
        self.audit = AuditLog([JsonlStdoutSink()])
        self.policy = PolicyEngine(
            PolicyConfig(
                allow_commands=True,
                allow_insecure_tls=False,
                max_payload_bytes=256_000,
            )
        )
        self.runtime = BridgeRuntime(cfg=self.cfg, metrics=self.metrics)

    def start(self) -> None:
        self.runtime.start()

    def stop(self) -> None:
        self.runtime.stop()

    def run_forever(self) -> None:
        # If you want policy gating of commands, wire it into CommandsController here
        self.runtime.run_forever()
