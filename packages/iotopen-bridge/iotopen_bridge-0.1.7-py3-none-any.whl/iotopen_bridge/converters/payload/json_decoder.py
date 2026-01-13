# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/payload/json_decoder.py
from __future__ import annotations

import json
import math
from typing import Any

from ...core.errors import ValidationError
from ...security.validation.json_safety import validate_json_value
from ...security.validation.limits import Limits, enforce_payload

BytesLike = bytes | bytearray | memoryview


def _reject_constants(x: str) -> Any:
    # Called for NaN/Infinity/-Infinity tokens
    raise ValidationError(f"invalid JSON constant: {x}")


class JsonDecoder:
    """Decode JSON payloads with strictness + safety limits."""

    def __init__(self, limits: Limits | None = None, *, strict: bool = True) -> None:
        self.strict = bool(strict)
        self.limits = limits if limits is not None else Limits()

    def decode(self, payload: BytesLike | str) -> Any:
        b = enforce_payload(payload, self.limits)

        try:
            s = b.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValidationError("payload is not valid UTF-8") from e

        try:
            obj = json.loads(s, parse_constant=_reject_constants) if self.strict else json.loads(s)
        except ValidationError:
            raise
        except json.JSONDecodeError as e:
            raise ValidationError(f"invalid JSON: {e.msg}") from e
        except Exception as e:
            raise ValidationError("invalid JSON") from e

        if self.strict:
            self._reject_nonfinite(obj)

        validate_json_value(obj, limits=self.limits)
        return obj

    def _reject_nonfinite(self, obj: Any) -> None:
        stack: list[Any] = [obj]
        while stack:
            node = stack.pop()
            if isinstance(node, float):
                if not math.isfinite(node):
                    raise ValidationError("non-finite float in JSON")
            elif isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                stack.extend(node.values())
