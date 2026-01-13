# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/audit/sinks.py
from __future__ import annotations

import contextlib
import json
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TextIO


class AuditSink:
    """Sink interface for structured audit events."""

    def emit(self, record: dict[str, Any]) -> None:  # pragma: no cover (interface)
        raise NotImplementedError


@dataclass
class JsonlStdoutSink(AuditSink):
    """Write one JSON object per line to stdout (or another stream)."""

    stream: TextIO = sys.stdout
    _lock: threading.RLock = field(
        default_factory=threading.RLock, init=False, repr=False, compare=False
    )

    def emit(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        with self._lock, contextlib.suppress(Exception):
            self.stream.write(line + "\n")
            self.stream.flush()


@dataclass
class JsonlFileSink(AuditSink):
    """Write one JSON object per line to a file, with size-based rotation."""

    path: str
    max_bytes: int = 10_000_000

    _fh: TextIO | None = field(default=None, init=False, repr=False, compare=False)
    _lock: threading.RLock = field(
        default_factory=threading.RLock, init=False, repr=False, compare=False
    )

    def _open(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        # Long-lived handle by design (rotation); SIM115 not applicable.
        self._fh = open(self.path, "a", encoding="utf-8")  # noqa: SIM115

    def _rotate_if_needed(self) -> None:
        p = Path(self.path)
        if p.exists() and p.stat().st_size > int(self.max_bytes):
            ts = time.strftime("%Y%m%d-%H%M%S")
            p.rename(p.with_name(p.name + "." + ts))
            if self._fh is not None:
                with contextlib.suppress(Exception):
                    self._fh.close()
                self._fh = None

    def emit(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            if self._fh is None:
                self._open()
            self._rotate_if_needed()

            assert self._fh is not None
            with contextlib.suppress(Exception):
                self._fh.write(line + "\n")
                self._fh.flush()
