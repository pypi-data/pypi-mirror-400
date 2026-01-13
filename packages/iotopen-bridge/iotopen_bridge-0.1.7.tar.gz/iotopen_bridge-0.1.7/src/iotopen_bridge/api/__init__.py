# SPDX-License-Identifier: Apache-2.0
"""Optional higher-level app wrapper.

`BridgeApp` is a small convenience wrapper used by the CLI supervisor mode.

The HTTP API routes under `iotopen_bridge.api.routes` are intentionally kept
decoupled from any specific web framework dependency.
"""

from .app import BridgeApp

__all__ = ["BridgeApp"]
