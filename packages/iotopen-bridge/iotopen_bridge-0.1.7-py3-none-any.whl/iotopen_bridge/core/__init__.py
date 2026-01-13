# File: src/iotopen_bridge/core/__init__.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

# Keep __init__ lightweight to avoid import-time side effects.
# Export commonly used error types from one place.
from .errors import (
    AggregateError,
    BridgeError,
    ConfigError,
    DecodeError,
    LynxError,
    NotFoundError,
    PolicyDenied,
    StorageError,
    ValidationError,
)

__all__ = [
    "AggregateError",
    "BridgeError",
    "ConfigError",
    "DecodeError",
    "LynxError",
    "NotFoundError",
    "PolicyDenied",
    "StorageError",
    "ValidationError",
]
