# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/lynx/mock_server.py
from __future__ import annotations

import argparse
import contextlib
import json
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse


@dataclass(frozen=True)
class MockLynxConfig:
    host: str = "127.0.0.1"
    # Allow port=0 for ephemeral port (useful in tests)
    port: int = 8787
    installation_id: int = 2222
    pretty: bool = True


@dataclass(frozen=True)
class MockLynxData:
    """Deterministic inventory payloads for the mock Lynx server.

    tests/integration/test_e2e_bridge_with_mock_lynx.py expects this type.
    """

    functions_by_installation: dict[int, list[dict[str, Any]]] = field(default_factory=dict)
    devices_by_installation: dict[int, list[dict[str, Any]]] = field(default_factory=dict)


def _default_functions(iid: int) -> list[dict[str, Any]]:
    """Return a minimal FunctionX-like payload that your bridge can ingest."""
    return [
        {
            "function_id": 508312,
            "installation_id": iid,
            "device_id": 30700,
            "type": "switch",
            "friendly_name": f"IoT Open Installation {iid} HA Zigbee Plug",
            "topic_read": f"{iid}/obj/generated/ha/zigbee_plug/state",
            "topic_set": f"{iid}/set/obj/generated/ha/zigbee_plug/state",
            "state_on": 1,
            "state_off": 0,
            "attribution": "Data via Mock Lynx",
        },
        {
            "function_id": 506179,
            "installation_id": iid,
            "device_id": 30700,
            "type": "alarm_power_management",
            "friendly_name": f"IoT Open Installation {iid} Power Alarm",
            "topic_read": f"{iid}/obj/generated/c96879ef-b7d5-4acb-a0b5-8911c0e3dc17",
            "topic_set": None,
            "attribution": "Data via Mock Lynx",
        },
    ]


def _normalize_function_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Best-effort normalization so tests can use 'name' but bridge can use 'friendly_name'."""
    out = dict(d)
    if "friendly_name" not in out and "name" in out:
        out["friendly_name"] = out.get("name")
    return out


def _json_bytes(obj: Any, *, pretty: bool) -> bytes:
    if pretty:
        return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")


class _Handler(BaseHTTPRequestHandler):
    cfg: MockLynxConfig
    data: MockLynxData

    def _send_json(self, code: int, body: Any) -> None:
        data = _json_bytes(body, pretty=bool(self.cfg.pretty))
        self.send_response(int(code))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path or "")
        path = (parsed.path or "").rstrip("/")
        qs = parse_qs(parsed.query or "")

        if path in ("", "/", "/health", "/healthz", "/readyz"):
            self._send_json(200, {"ok": True, "service": "mock-lynx"})
            return

        lower = path.lower()

        if "functionx" in lower:
            iid = self._extract_installation_id(path, qs)
            funcs = self.data.functions_by_installation.get(iid)
            if funcs is None:
                funcs = _default_functions(iid)
            funcs_norm = [_normalize_function_dict(x) for x in funcs]
            self._send_json(200, funcs_norm)
            return

        if "devicex" in lower:
            iid = self._extract_installation_id(path, qs)
            devs = self.data.devices_by_installation.get(iid, [])
            self._send_json(200, devs)
            return

        self._send_json(404, {"ok": False, "error": "not_found", "path": path})

    def _extract_installation_id(self, path: str, qs: dict[str, list[str]]) -> int:
        for key in ("installationId", "installation_id", "iid"):
            if qs.get(key):
                with contextlib.suppress(Exception):
                    return int(qs[key][0])

        parts = [p for p in path.split("/") if p]
        if parts:
            tail = parts[-1]
            with contextlib.suppress(Exception):
                return int(tail)

        return int(self.cfg.installation_id)

    def log_message(self, fmt: str, *args: Any) -> None:
        return


class MockLynxServer:
    """Tiny HTTP server that mimics a subset of Lynx endpoints."""

    def __init__(
        self, cfg: MockLynxConfig | None = None, *, data: MockLynxData | None = None
    ) -> None:
        self.cfg = cfg or MockLynxConfig()
        self.data = data or MockLynxData()
        self._httpd: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def base_url(self) -> str:
        host, port = self.host_port
        return f"http://{host}:{port}"

    @property
    def host_port(self) -> tuple[str, int]:
        if self._httpd is None:
            return (self.cfg.host, int(self.cfg.port))

        # server_address may be (host, port) or (host, port, flowinfo, scopeid) on IPv6.
        addr = self._httpd.server_address
        host = str(addr[0])
        port = int(addr[1])
        return (host, port)

    def start(self) -> tuple[str, int]:
        if self._httpd is not None:
            return self.host_port

        handler_cls = type("MockLynxHandler", (_Handler,), {})
        handler_cls.cfg = self.cfg  # type: ignore[attr-defined]
        handler_cls.data = self.data  # type: ignore[attr-defined]

        self._httpd = HTTPServer((self.cfg.host, int(self.cfg.port)), handler_cls)
        self._httpd.timeout = 0.5  # type: ignore[attr-defined]

        t = threading.Thread(
            target=self._httpd.serve_forever, name="iotopen-mock-lynx", daemon=True
        )
        self._thread = t
        t.start()

        return self.host_port

    def stop(self) -> None:
        httpd = self._httpd
        self._httpd = None
        if httpd is None:
            return
        with contextlib.suppress(Exception):
            httpd.shutdown()
        with contextlib.suppress(Exception):
            httpd.server_close()


def _parse_args(argv: list[str] | None = None) -> MockLynxConfig:
    p = argparse.ArgumentParser(prog="python -m iotopen_bridge.lynx.mock_server")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8787)
    p.add_argument("--installation-id", type=int, default=2222)
    p.add_argument("--no-pretty", action="store_true", help="Disable pretty JSON output")
    ns = p.parse_args(argv)
    return MockLynxConfig(
        host=str(ns.host),
        port=int(ns.port),
        installation_id=int(ns.installation_id),
        pretty=not bool(ns.no_pretty),
    )


def main(argv: list[str] | None = None) -> int:
    cfg = _parse_args(argv)
    srv = MockLynxServer(cfg=cfg)
    host, port = srv.start()
    print(f"[mock-lynx] listening on http://{host}:{port} (installation_id={cfg.installation_id})")
    print(
        "[mock-lynx] endpoints: /api/functionx, /api/v1/functionx, /api/vw/functionx, /api/v2/functionx/<iid>"
    )
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        srv.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
