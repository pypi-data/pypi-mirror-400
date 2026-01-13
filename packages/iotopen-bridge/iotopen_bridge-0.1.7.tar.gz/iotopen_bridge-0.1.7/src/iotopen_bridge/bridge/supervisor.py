# File: src/iotopen_bridge/bridge/supervisor.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
import logging
import random
import threading
from dataclasses import dataclass, field
from typing import Protocol

from ..core.backoff import Backoff
from ..core.clock import MonotonicClock
from ..observability.metrics import Metrics
from ..security.audit.audit_log import AuditLog

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SupervisorConfig:
    """Run-loop policy for robust operation."""

    restart_on_crash: bool = True

    # Exponential backoff for crash loops
    backoff: Backoff = field(default_factory=lambda: Backoff(base=1.0, cap=30.0, factor=2.0))
    jitter_ratio: float = 0.25  # +/- 25%

    # Supervisor tick while waiting (also used for stop responsiveness)
    tick_seconds: float = 0.25

    # Optional circuit-breaker (prevents infinite restart loops in prod)
    max_restarts: int | None = None
    restart_window_seconds: float = 300.0  # count restarts within this sliding window


class BridgeApp(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def run_forever(self) -> None: ...


class Supervisor:
    """Crash-safe supervisor with exponential backoff + jitter.

    You get:
      - start/stop lifecycle
      - crash -> backoff -> restart (optional)
      - optional circuit-breaker for runaway crash loops
      - metrics + audit hooks
    """

    def __init__(
        self,
        app: BridgeApp,
        *,
        cfg: SupervisorConfig | None = None,
        metrics: Metrics | None = None,
        audit: AuditLog | None = None,
    ) -> None:
        self.app = app
        self.cfg = cfg or SupervisorConfig()
        self.metrics = metrics
        self.audit = audit

        self._clock = MonotonicClock()
        self._stop = threading.Event()

        # sliding window of restart timestamps (monotonic seconds)
        self._restart_ts: list[float] = []

    def request_stop(self) -> None:
        self._stop.set()

    def _audit(
        self,
        event: str,
        *,
        outcome: str = "ok",
        severity: str = "info",
        details: dict | None = None,
    ) -> None:
        if not self.audit:
            return
        with contextlib.suppress(Exception):
            self.audit.write(event, outcome=outcome, severity=severity, details=details or {})

    def run(self) -> None:
        backoff = self.cfg.backoff
        backoff.reset()

        while not self._stop.is_set():
            try:
                self._audit(
                    "supervisor_start", details={"restart_on_crash": self.cfg.restart_on_crash}
                )
                if self.metrics:
                    self.metrics.inc("supervisor_start_total")

                # Some apps want a distinct start() step; keep it optional but supported.
                try:
                    self.app.start()
                except Exception:
                    # If app doesn't implement start semantics cleanly, run_forever may still work.
                    _LOGGER.debug(
                        "app.start() raised; continuing into run_forever()", exc_info=True
                    )

                self.app.run_forever()

                # If run_forever returns normally, treat as intentional shutdown.
                if self.metrics:
                    self.metrics.inc("supervisor_exit_clean_total")
                self._audit("supervisor_exit_clean")
                return

            except Exception as e:
                if self.metrics:
                    self.metrics.inc("supervisor_crash_total")
                self._audit(
                    "supervisor_crash",
                    outcome="error",
                    severity="error",
                    details={"error": str(e), "type": type(e).__name__},
                )

                _LOGGER.exception("Bridge crashed: %s", e)

                try:
                    self.app.stop()
                except Exception:
                    _LOGGER.debug("app.stop() raised during crash cleanup", exc_info=True)

                if not self.cfg.restart_on_crash:
                    return

                # Circuit-breaker: too many restarts in a short window -> stop restarting.
                if self.cfg.max_restarts is not None:
                    now = float(self._clock.now())
                    window = float(self.cfg.restart_window_seconds)
                    self._restart_ts = [t for t in self._restart_ts if (now - t) <= window]
                    self._restart_ts.append(now)
                    if len(self._restart_ts) > int(self.cfg.max_restarts):
                        _LOGGER.error(
                            "Supervisor circuit-breaker tripped: %d restarts within %.1fs (max=%d). Stopping.",
                            len(self._restart_ts),
                            window,
                            int(self.cfg.max_restarts),
                        )
                        if self.metrics:
                            self.metrics.inc("supervisor_circuit_breaker_total")
                        self._audit(
                            "supervisor_circuit_breaker",
                            outcome="error",
                            severity="error",
                            details={"restarts": len(self._restart_ts), "window_seconds": window},
                        )
                        return

                delay = float(backoff.next())

                # Jitter: randomize restart to avoid thundering herd in fleets
                jitter = delay * float(self.cfg.jitter_ratio)
                delay = max(0.0, delay + random.uniform(-jitter, jitter))

                if self.metrics:
                    self.metrics.set_gauge("supervisor_backoff_seconds", delay)

                # Wait (interruptible)
                self._stop.wait(timeout=max(0.0, delay))

        # stop requested
        self._audit("supervisor_stop_requested")
        try:
            self.app.stop()
        except Exception:
            _LOGGER.debug("app.stop() raised during stop request", exc_info=True)
