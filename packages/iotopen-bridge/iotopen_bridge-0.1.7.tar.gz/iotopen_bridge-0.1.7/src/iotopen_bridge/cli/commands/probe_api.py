# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/cli/commands/probe_api.py
from __future__ import annotations

import asyncio
import inspect
import json
from typing import Any

from ...bridge.config import BridgeConfig
from ...lynx.auth import LynxAuth
from ...lynx.client import LynxApiClient


def _resolve(maybe_awaitable: Any) -> Any:
    if inspect.isawaitable(maybe_awaitable):

        async def _aw() -> Any:
            return await maybe_awaitable

        return asyncio.run(_aw())
    return maybe_awaitable


def cmd_probe_api(args: Any) -> int:
    """Call Lynx API endpoints and print results as JSON."""
    cfg = BridgeConfig.from_file(args.config)
    api = LynxApiClient(base_url=cfg.lynx.base_url, auth=LynxAuth(cfg.lynx.api_key))

    fx_list = _resolve(api.list_functions(int(cfg.lynx.installation_id))) or []
    fx_payload = [getattr(f, "__dict__", f) for f in fx_list]
    print(json.dumps(fx_payload, ensure_ascii=False, indent=2))

    # Optional: only call if method exists
    if hasattr(api, "get_status"):
        status = _resolve(api.get_status(int(cfg.lynx.installation_id)))
        print(json.dumps(getattr(status, "__dict__", status), ensure_ascii=False, indent=2))

    return 0
