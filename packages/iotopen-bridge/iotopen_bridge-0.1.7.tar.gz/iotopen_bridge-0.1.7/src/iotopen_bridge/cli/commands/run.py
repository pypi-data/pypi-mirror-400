from __future__ import annotations

import argparse
import contextlib
import signal
import sys

from ...bridge.config import BridgeConfig
from ...bridge.runtime import BridgeRuntime


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="iotopen-bridge run", description="Run IoT Open Bridge")
    p.add_argument("--config", required=True, help="Path to config.yml / .json / .toml")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    cfg = BridgeConfig.load(args.config)
    runtime = BridgeRuntime(cfg)

    def _stop(_signum, _frame) -> None:
        runtime.stop()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    runtime.start()
    runtime.run_forever()
    return 0


def cmd_run(args) -> int:
    """Console entry for `iotopen-bridge run` subcommand."""

    cfg = BridgeConfig.load(args.config)
    runtime = BridgeRuntime(cfg)

    def _stop(_signum, _frame) -> None:
        runtime.stop()

    # Windows may not support all signals - keep it best-effort.
    with contextlib.suppress(Exception):
        signal.signal(signal.SIGINT, _stop)
    with contextlib.suppress(Exception):
        signal.signal(signal.SIGTERM, _stop)

    runtime.start()
    runtime.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
