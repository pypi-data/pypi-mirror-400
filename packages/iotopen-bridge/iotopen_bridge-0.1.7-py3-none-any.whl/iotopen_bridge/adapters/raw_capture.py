# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/adapters/raw_capture.py
from __future__ import annotations

import contextlib
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO


@dataclass(frozen=True)
class RawCaptureConfig:
    enabled: bool = False
    directory: str = "./state/capture"
    max_bytes_per_file: int = 5_000_000
    prefix: str = "mqtt"


class RawCapture:
    """Best-effort raw capture of MQTT payloads (RX/TX) to rotating files."""

    def __init__(self, cfg: RawCaptureConfig) -> None:
        self.cfg = cfg
        self._lock = threading.RLock()
        self._fh: BinaryIO | None = None
        self._path: Path | None = None
        self._written = 0

    def _open_if_needed(self) -> None:
        if not self.cfg.enabled:
            return

        with self._lock:
            if self._fh is not None:
                return

            Path(self.cfg.directory).mkdir(parents=True, exist_ok=True)
            ts = time.strftime("%Y%m%d-%H%M%S")
            fname = f"{self.cfg.prefix}-{ts}-{os.getpid()}.log"
            path = Path(self.cfg.directory) / fname
            self._path = path
            self._fh = open(path, "ab", buffering=0)  # noqa: SIM115
            self._written = 0

    def _rotate_if_needed(self) -> None:
        if not self.cfg.enabled:
            return
        with self._lock:
            if self._fh is None:
                return
            if self._written < int(self.cfg.max_bytes_per_file):
                return
            with contextlib.suppress(Exception):
                self._fh.close()
            self._fh = None
            self._path = None
            self._written = 0

    def _write_line(self, line: bytes) -> None:
        if not self.cfg.enabled:
            return
        self._open_if_needed()
        with self._lock:
            fh = self._fh
            if fh is None:
                return
            with contextlib.suppress(Exception):
                fh.write(line)
                self._written += len(line)
        self._rotate_if_needed()

    def capture_rx(self, topic: str, payload: bytes, qos: int, retain: bool) -> None:
        if not self.cfg.enabled:
            return
        meta = f"RX topic={topic} qos={qos} retain={retain} bytes={len(payload)}\n".encode(
            "utf-8", "ignore"
        )
        self._write_line(meta + payload + b"\n\n")

    def capture_tx(self, topic: str, payload: bytes, qos: int, retain: bool) -> None:
        if not self.cfg.enabled:
            return
        meta = f"TX topic={topic} qos={qos} retain={retain} bytes={len(payload)}\n".encode(
            "utf-8", "ignore"
        )
        self._write_line(meta + payload + b"\n\n")

    # ---- compatibility adapter for older/newer call-sites ----
    def capture_mqtt_message(self, *args: Any, **kwargs: Any) -> None:
        """Compatibility shim.

        Accepts common call shapes such as:
          - capture_mqtt_message("rx", topic, payload, qos, retain, meta=...)
          - capture_mqtt_message(direction="rx", topic=..., payload=..., qos=..., retain=..., meta=...)
        """
        if not self.cfg.enabled:
            return

        direction = kwargs.pop("direction", None) or kwargs.pop("dir", None)
        topic = kwargs.pop("topic", None)
        payload = kwargs.pop("payload", None)
        qos = kwargs.pop("qos", 0)
        retain = kwargs.pop("retain", False)
        _ = kwargs.pop("meta", None)  # meta is accepted but not persisted right now

        # Positional forms
        if args:
            # ("rx", topic, payload, qos, retain, ...)
            if (
                isinstance(args[0], str)
                and args[0].strip().lower() in {"rx", "tx"}
                and len(args) >= 3
            ):
                direction = args[0]
                topic = args[1]
                payload = args[2]
                if len(args) >= 4:
                    qos = args[3]
                if len(args) >= 5:
                    retain = args[4]
            else:
                # (topic, payload, qos, retain, ...)
                topic = topic if topic is not None else (args[0] if len(args) >= 1 else None)
                payload = payload if payload is not None else (args[1] if len(args) >= 2 else None)
                if len(args) >= 3:
                    qos = args[2]
                if len(args) >= 4:
                    retain = args[3]

        t = str(topic or "")
        q = int(qos or 0)
        r = bool(retain)

        b: bytes
        if payload is None:
            b = b""
        elif isinstance(payload, (bytes, bytearray)):
            b = bytes(payload)
        elif isinstance(payload, memoryview):
            b = payload.tobytes()
        else:
            b = str(payload).encode("utf-8", "ignore")

        d = str(direction or "rx").strip().lower()
        if d == "tx":
            self.capture_tx(t, b, q, r)
        else:
            self.capture_rx(t, b, q, r)
