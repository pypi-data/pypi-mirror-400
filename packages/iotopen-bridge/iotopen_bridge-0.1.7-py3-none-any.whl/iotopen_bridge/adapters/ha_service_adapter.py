# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/adapters/ha_service_adapter.py
from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import Any

from ..controllers.commands import CommandsController


@dataclass(frozen=True)
class HaServiceAdapterConfig:
    """
    - domain: HA service domain, e.g. "iotopen"
    - require_config_entry_id: if True, calls must include matching config_entry_id
    """

    domain: str = "iotopen_bridge"
    require_config_entry_id: bool = False


class HaServiceAdapter:
    """
    Registers HA services mapping -> CommandsController.
    Home Assistant imports are lazy to keep standalone mode clean.
    """

    def __init__(self, cfg: HaServiceAdapterConfig) -> None:
        self.cfg = cfg
        self._registered = False

    async def async_register(
        self,
        hass: Any,
        commands: CommandsController,
        *,
        config_entry_id: str | None = None,
    ) -> None:
        if self._registered:
            return

        domain = self.cfg.domain

        try:
            import voluptuous as vol  # type: ignore
        except Exception:
            vol = None

        async def _handle_send_switch(call: Any) -> None:
            data = getattr(call, "data", {}) or {}

            if self.cfg.require_config_entry_id:
                if not config_entry_id:
                    return
                if str(data.get("config_entry_id", "")) != str(config_entry_id):
                    return

            try:
                function_id = int(data["function_id"])
            except Exception:
                return

            on = bool(data.get("on"))
            commands.send_switch(function_id, on)

        schema = None
        if vol is not None:
            schema = vol.Schema(
                {
                    vol.Required("function_id"): int,
                    vol.Required("on"): bool,
                    vol.Optional("config_entry_id"): str,
                }
            )

        hass.services.async_register(domain, "send_switch", _handle_send_switch, schema=schema)
        self._registered = True

    async def async_unregister(self, hass: Any) -> None:
        if not self._registered:
            return

        domain = self.cfg.domain

        # In HA core, async_remove is not awaitable.
        with contextlib.suppress(Exception):
            hass.services.async_remove(domain, "send_switch")

        self._registered = False
