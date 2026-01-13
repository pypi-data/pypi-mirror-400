# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/payload/scalar_decoder.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ...core.errors import ValidationError
from ...security.validation.limits import Limits, enforce_payload
from ..normalize.bool import to_bool
from ..normalize.number import to_float, to_int
from .base import DecodeError, DecoderContext


@dataclass(frozen=True)
class ScalarDecoder:
    """Decode common scalars from bytes/text.

    Order:
      1) bool-ish
      2) int
      3) float
      4) utf-8 text
    """

    limits: Limits = field(default_factory=Limits)
    encoding: str = "utf-8"
    errors: str = "ignore"

    def decode(
        self,
        payload: bytes | bytearray | memoryview | str,
        *,
        topic: str | None = None,
        ctx: DecoderContext | None = None,
    ) -> Any:
        try:
            b = enforce_payload(payload, self.limits)
        except ValidationError as e:
            raise DecodeError(str(e)) from e

        try:
            s = b.decode(self.encoding, self.errors).strip()
        except Exception as e:
            raise DecodeError(f"decode failed: {e}") from e

        if s == "":
            raise DecodeError("empty payload")

        bval = to_bool(s)
        if bval is not None:
            return bval

        ival = to_int(s)
        if ival is not None:
            return ival

        fval = to_float(s)
        if fval is not None:
            return fval

        return s
