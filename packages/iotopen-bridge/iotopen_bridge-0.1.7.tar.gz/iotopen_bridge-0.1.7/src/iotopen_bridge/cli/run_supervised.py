# File: src/iotopen_bridge/cli/run_supervised.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

from ..api.app import BridgeApp
from ..bridge.config import BridgeConfig
from ..bridge.supervisor import Supervisor, SupervisorConfig
from ..observability.logging import configure_logging
from ..observability.metrics import Metrics


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="iotopen-bridge-supervised")
    p.add_argument("--config", default="config.json")
    args = p.parse_args(argv)

    cfg = BridgeConfig.load(args.config)
    configure_logging(cfg.log_level)

    metrics = Metrics()
    app = BridgeApp(cfg=cfg, metrics=metrics)

    sup = Supervisor(
        app, cfg=SupervisorConfig(restart_on_crash=True), metrics=metrics, audit=app.audit
    )
    sup.run()
