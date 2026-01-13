# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/payload/base.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from ...core.errors import ValidationError


class DecodeError(ValidationError):
    """Raised when a payload cannot be decoded safely."""


@dataclass(frozen=True)
class DecoderContext:
    topic: str | None = None


@runtime_checkable
class PayloadDecoder(Protocol):
    """Decode raw MQTT payload into a Python value."""

    def decode(
        self,
        payload: bytes | bytearray | memoryview | str,
        *,
        topic: str | None = None,
        ctx: DecoderContext | None = None,
    ) -> Any: ...
