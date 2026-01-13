# File: src/iotopen_bridge/observability/logging.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone

from opentelemetry import trace


class _JsonFormatter(logging.Formatter):
    """Structured JSON logs without extra dependencies."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "thread": record.threadName,
        }

        # Trace correlation (when available/active)
        try:
            span = trace.get_current_span()
            ctx = span.get_span_context()
            if ctx and ctx.is_valid:
                payload["trace_id"] = f"{ctx.trace_id:032x}"
                payload["span_id"] = f"{ctx.span_id:016x}"
        except Exception:
            # Never break logging.
            pass

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            payload["extra"] = extra

        return json.dumps(payload, ensure_ascii=False)


def _env_bool(name: str, default: bool = False) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    if not v:
        return default
    return v in {"1", "true", "t", "yes", "y", "on"}


def configure_logging(level: str | None = None) -> None:
    """Configure root logging.

    Env overrides:
      - IOTOPEN_BRIDGE_LOG_LEVEL   (default INFO)
      - IOTOPEN_BRIDGE_LOG_JSON    (default false)
      - IOTOPEN_BRIDGE_LOG_FILE    (optional file path)
      - IOTOPEN_BRIDGE_LOG_FORCE   (default true on py>=3.8)
      - IOTOPEN_BRIDGE_LOG_NOISY   (default false; if false, down-level chatty deps)
    """
    lvl = (level or os.environ.get("IOTOPEN_BRIDGE_LOG_LEVEL") or "INFO").upper()
    use_json = _env_bool("IOTOPEN_BRIDGE_LOG_JSON", False)
    log_file = (os.environ.get("IOTOPEN_BRIDGE_LOG_FILE") or "").strip() or None
    noisy = _env_bool("IOTOPEN_BRIDGE_LOG_NOISY", False)

    force_default = True
    force = _env_bool("IOTOPEN_BRIDGE_LOG_FORCE", force_default)

    root_level = getattr(logging, lvl, logging.INFO)

    handlers: list[logging.Handler] = []

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    if use_json:
        stream_handler.setFormatter(_JsonFormatter())
    else:
        stream_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s.%(msecs)03d %(levelname)s %(name)s [%(threadName)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    handlers.append(stream_handler)

    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(_JsonFormatter() if use_json else stream_handler.formatter)
        handlers.append(fh)

    try:
        logging.basicConfig(level=root_level, handlers=handlers, force=bool(force))  # py>=3.8
    except TypeError:
        logging.basicConfig(level=root_level, handlers=handlers)

    if not noisy:
        for name in (
            "urllib3.connectionpool",
            "urllib3.util.retry",
            "paho",
        ):
            logging.getLogger(name).setLevel(logging.WARNING)
