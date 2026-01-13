# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/transport/http/aiohttp_client.py
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import aiohttp


class AioHttpClient:
    async def get_json(self, url: str, headers: Mapping[str, str], timeout: float = 15.0) -> Any:
        async with (
            aiohttp.ClientSession() as session,
            session.get(url, headers=dict(headers), timeout=timeout) as resp,
        ):
            resp.raise_for_status()
            return await resp.json()
