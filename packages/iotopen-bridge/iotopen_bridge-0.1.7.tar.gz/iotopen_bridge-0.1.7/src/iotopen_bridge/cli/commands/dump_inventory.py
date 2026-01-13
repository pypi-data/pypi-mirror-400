# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/cli/commands/dump_inventory.py
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


def cmd_dump_inventory(args: Any) -> int:
    """Fetch Function inventory from Lynx and print it."""
    cfg = BridgeConfig.from_file(args.config)
    api = LynxApiClient(base_url=cfg.lynx.base_url, auth=LynxAuth(cfg.lynx.api_key))

    # Prefer the runtime naming: list_functions()
    res = _resolve(api.list_functions(int(cfg.lynx.installation_id)))
    if res is None:
        print("[]")
        return 0

    if isinstance(res, list):
        out = []
        for x in res:
            out.append(getattr(x, "__dict__", x))
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print(json.dumps(getattr(res, "__dict__", res), ensure_ascii=False, indent=2))
    return 0
