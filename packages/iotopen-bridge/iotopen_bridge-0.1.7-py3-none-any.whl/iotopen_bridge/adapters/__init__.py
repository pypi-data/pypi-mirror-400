# SPDX-License-Identifier: Apache-2.0
"""Adapters package.

Do NOT eagerly import submodules here. Importing iotopen_bridge.adapters.<module>
executes this __init__.py first, and eager imports can create circular imports
(e.g. bridge.config -> adapters -> controllers -> bridge.config).

We expose selected names via lazy attribute access (PEP 562).
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

__all__ = [
    "HADiscoveryPublisher",
    "HaServiceAdapter",
    "HaServiceAdapterConfig",
    "MqttRouter",
    "RawCapture",
    "RawCaptureConfig",
]

_LAZY: dict[str, str] = {
    "HADiscoveryPublisher": "iotopen_bridge.adapters.ha_discovery_publisher",
    "HaServiceAdapter": "iotopen_bridge.adapters.ha_service_adapter",
    "HaServiceAdapterConfig": "iotopen_bridge.adapters.ha_service_adapter",
    "MqttRouter": "iotopen_bridge.adapters.mqtt_router",
    "RawCapture": "iotopen_bridge.adapters.raw_capture",
    "RawCaptureConfig": "iotopen_bridge.adapters.raw_capture",
}

if TYPE_CHECKING:  # pragma: no cover
    from .ha_discovery_publisher import HADiscoveryPublisher as HADiscoveryPublisher
    from .ha_service_adapter import HaServiceAdapter as HaServiceAdapter
    from .ha_service_adapter import HaServiceAdapterConfig as HaServiceAdapterConfig
    from .mqtt_router import MqttRouter as MqttRouter
    from .raw_capture import RawCapture as RawCapture
    from .raw_capture import RawCaptureConfig as RawCaptureConfig


def __getattr__(name: str) -> Any:
    mod = _LAZY.get(name)
    if not mod:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(mod)
    return getattr(module, name)


def __dir__() -> list[str]:
    return sorted([*globals().keys(), *_LAZY.keys()])
