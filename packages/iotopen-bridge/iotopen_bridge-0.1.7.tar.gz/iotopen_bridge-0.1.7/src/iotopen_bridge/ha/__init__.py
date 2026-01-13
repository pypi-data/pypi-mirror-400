# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/ha/__init__.py

"""Home Assistant integration helpers.

This package is **optional**: it does not require Home Assistant at install-time,
but it provides thin helpers that make Home Assistant custom components much smaller.

Typical usage inside a HA custom integration:

    from iotopen_bridge.ha import HABridgeHandle, build_bridge_config

    cfg = build_bridge_config(
        base_url=...,
        api_key=...,
        installation_id=...,
        mqtt_host=...,
        mqtt_port=...,
    )
    handle = HABridgeHandle.from_config(cfg)
    await handle.async_start(hass)
"""

from .facade import HABridgeHandle, build_bridge_config

__all__ = ["HABridgeHandle", "build_bridge_config"]
