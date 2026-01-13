# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/cli/main.py
from __future__ import annotations

import argparse
import json
import os
from typing import Any

from ..bridge.config import BridgeConfig
from ..bridge.runtime import BridgeRuntime
from ..observability.logging import configure_logging
from ..observability.metrics import Metrics


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True))


def _cmd_doctor(args: argparse.Namespace) -> int:
    cfg = BridgeConfig.load(args.config)

    # Basic config validation already happens inside load()
    out: dict[str, Any] = {
        "ok": True,
        "config": str(args.config),
        "pid": int(os.getpid()),
        "mqtt": {"host": cfg.mqtt.host, "port": int(cfg.mqtt.port)},
        "lynx": {"base_url": cfg.lynx.base_url, "installation_id": int(cfg.lynx.installation_id)},
        "authz": {
            "mode": str(cfg.authz.mode),
            "allow_prefixes": len(cfg.authz.allow_prefixes),
            "allow_topics": len(cfg.authz.allow_topics),
            "deny_prefixes": len(cfg.authz.deny_prefixes),
        },
    }

    _print_json(out)
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    cfg = BridgeConfig.load(args.config)
    configure_logging(cfg.log_level)  # <- add this
    metrics = Metrics(enabled=True)

    rt = BridgeRuntime(cfg=cfg, metrics=metrics)
    return int(rt.run())


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="iotopen-bridge")
    p.add_argument("-c", "--config", default=None, help="Config file path (yaml/json/toml)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_doctor = sub.add_parser("doctor", help="Validate config and show effective settings")
    p_doctor.set_defaults(fn=_cmd_doctor)

    p_run = sub.add_parser("run", help="Run the bridge")
    p_run.set_defaults(fn=_cmd_run)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    fn = getattr(args, "fn", None)
    if fn is None:
        parser.print_help()
        return 2
    return int(fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
