# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/bridge/health_http.py
from __future__ import annotations

import contextlib
import json
import threading
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

StatusFn = Callable[[], dict[str, Any]]
MetricsFn = Callable[[], str]


@dataclass
class HealthServer:
    host: str
    port: int
    status_fn: StatusFn
    metrics_fn: MetricsFn | None = None

    _srv: HTTPServer | None = None
    _thread: threading.Thread | None = None

    def start(self) -> None:
        if self._srv is not None:
            return

        status_fn = self.status_fn
        metrics_fn = self.metrics_fn

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                # keep test output clean
                return

            def _send(self, code: int, body: bytes, *, content_type: str) -> None:
                self.send_response(int(code))
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:
                path = urlparse(self.path).path

                if path == "/metrics":
                    if callable(metrics_fn):
                        text = metrics_fn()
                        b = text.encode("utf-8", errors="replace")
                        self._send(200, b, content_type="text/plain; version=0.0.4; charset=utf-8")
                        return

                    # test suite will skip if this string appears
                    b = b"prometheus_client not installed\n"
                    self._send(200, b, content_type="text/plain; charset=utf-8")
                    return

                if path in ("/healthz", "/readyz", "/"):
                    payload = status_fn()
                    b = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                    self._send(200, b, content_type="application/json; charset=utf-8")
                    return

                self._send(404, b"not found\n", content_type="text/plain; charset=utf-8")

        self._srv = HTTPServer((str(self.host), int(self.port)), Handler)

        def _run() -> None:
            assert self._srv is not None
            self._srv.serve_forever(poll_interval=0.2)

        self._thread = threading.Thread(target=_run, name="iotopen-bridge-health-http", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        srv = self._srv
        if srv is None:
            return

        with contextlib.suppress(Exception):
            srv.shutdown()
        with contextlib.suppress(Exception):
            srv.server_close()

        t = self._thread
        self._srv = None
        self._thread = None

        if t:
            with contextlib.suppress(Exception):
                t.join(timeout=2)
