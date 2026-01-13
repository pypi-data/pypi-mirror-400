# SPDX-License-Identifier: Apache-2.0
"""Controllers package.

Expose selected controller classes via lazy attribute access (PEP 562).
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

__all__ = [
    "CommandsController",
    "InventoryController",
    "TelemetryController",
]

_LAZY: dict[str, str] = {
    "CommandsController": "iotopen_bridge.controllers.commands",
    "InventoryController": "iotopen_bridge.controllers.inventory",
    "TelemetryController": "iotopen_bridge.controllers.telemetry",
}

if TYPE_CHECKING:  # pragma: no cover
    from .commands import CommandsController as CommandsController
    from .inventory import InventoryController as InventoryController
    from .telemetry import TelemetryController as TelemetryController


def __getattr__(name: str) -> Any:
    mod = _LAZY.get(name)
    if not mod:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(mod)
    return getattr(module, name)


def __dir__() -> list[str]:
    return sorted([*globals().keys(), *_LAZY.keys()])
