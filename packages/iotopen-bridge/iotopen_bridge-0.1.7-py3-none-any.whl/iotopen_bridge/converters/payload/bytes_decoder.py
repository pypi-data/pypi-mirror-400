# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/payload/bytes_decoder.py
from __future__ import annotations

from dataclasses import dataclass, field

from ...core.errors import ValidationError
from ...security.validation.limits import Limits, enforce_payload
from .base import DecodeError, DecoderContext


@dataclass(frozen=True)
class BytesDecoder:
    """Return raw bytes or decoded text (optionally)."""

    as_text: bool = False
    encoding: str = "utf-8"
    errors: str = "strict"
    limits: Limits = field(default_factory=Limits)

    def decode(
        self,
        payload: bytes | bytearray | memoryview | str,
        *,
        topic: str | None = None,
        ctx: DecoderContext | None = None,
    ):
        try:
            b = enforce_payload(payload, self.limits)
        except ValidationError as e:
            raise DecodeError(str(e)) from e

        if not self.as_text:
            return b

        try:
            return b.decode(self.encoding, self.errors)
        except Exception as e:
            raise DecodeError(f"text decode failed ({self.encoding}/{self.errors}): {e}") from e
