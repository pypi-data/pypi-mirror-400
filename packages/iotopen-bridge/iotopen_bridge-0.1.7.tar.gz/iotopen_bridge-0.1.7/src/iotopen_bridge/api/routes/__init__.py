# File: src/iotopen_bridge/api/routes/__init__.py
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from . import commands as _commands
from . import health as _health
from . import inventory as _inventory


def _call_register(mod: Any, app: Any, deps: Any) -> None:
    """Register module routes without hard-requiring a static 'register' symbol.

    Supports:
      - def register(app, deps) -> None
      - def register(app) -> None
      - FastAPI-style: module.router + app.include_router(router)
    """
    fn = getattr(mod, "register", None)
    if callable(fn):
        # Try (app, deps) first; fall back to (app).
        try:
            cast(Callable[..., Any], fn)(app, deps)
            return
        except TypeError:
            cast(Callable[..., Any], fn)(app)
            return

    router = getattr(mod, "router", None)
    include_router = getattr(app, "include_router", None)
    if router is not None and callable(include_router):
        include_router(router)
        return

    raise AttributeError(
        f"{getattr(mod, '__name__', mod)!r} exposes neither register(...) nor router for include_router()."
    )


def register(app: Any, deps: Any) -> None:
    _call_register(_health, app, deps)
    _call_register(_commands, app, deps)
    _call_register(_inventory, app, deps)


def register_health(app: Any, deps: Any) -> None:
    _call_register(_health, app, deps)


def register_commands(app: Any, deps: Any) -> None:
    _call_register(_commands, app, deps)


def register_inventory(app: Any, deps: Any) -> None:
    _call_register(_inventory, app, deps)


__all__ = ["register", "register_commands", "register_health", "register_inventory"]
