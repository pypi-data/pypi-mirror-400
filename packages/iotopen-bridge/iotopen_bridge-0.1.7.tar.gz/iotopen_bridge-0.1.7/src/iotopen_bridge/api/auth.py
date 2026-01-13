# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/api/auth.py
"""Backward-compatible alias to the canonical LynxAuth.

Prefer: `from iotopen_bridge.lynx.auth import LynxAuth`
"""

from __future__ import annotations

from ..lynx.auth import LynxAuth

__all__ = ["LynxAuth"]
