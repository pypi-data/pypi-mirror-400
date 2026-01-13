# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/validation/json_safety.py
from __future__ import annotations

import math
from typing import Any

from ...core.errors import ValidationError
from .limits import Limits


def validate_json_value(value: Any, *, limits: Limits | None = None) -> None:
    """Validate a parsed JSON value against defensive limits.

    This is iterative (no recursion) to avoid recursion depth attacks.
    """
    lim = limits or Limits()

    # Allowed scalar types in JSON
    allowed_scalars = (type(None), bool, int, float, str)

    total_items = 0
    stack: list[tuple[Any, int]] = [(value, 1)]

    while stack:
        node, depth = stack.pop()

        if depth > int(lim.max_json_depth):
            raise ValidationError(f"json depth exceeded: {depth} > {lim.max_json_depth}")

        if isinstance(node, allowed_scalars):
            if isinstance(node, str) and len(node) > int(lim.max_string_chars):
                raise ValidationError(f"json string too long: {len(node)} > {lim.max_string_chars}")
            if isinstance(node, float) and not math.isfinite(node):
                raise ValidationError("non-finite float in json")
            continue

        if isinstance(node, list):
            if len(node) > int(lim.max_json_array_len):
                raise ValidationError(
                    f"json array too long: {len(node)} > {lim.max_json_array_len}"
                )
            total_items += len(node)
            if total_items > int(lim.max_json_total_items):
                raise ValidationError("json too large (total items)")
            for x in node:
                stack.append((x, depth + 1))
            continue

        if isinstance(node, dict):
            if len(node) > int(lim.max_json_keys):
                raise ValidationError(
                    f"json object too many keys: {len(node)} > {lim.max_json_keys}"
                )
            total_items += len(node)
            if total_items > int(lim.max_json_total_items):
                raise ValidationError("json too large (total items)")

            for k, v in node.items():
                if not isinstance(k, str):
                    raise ValidationError("json object key must be string")
                if len(k) > int(lim.max_string_chars):
                    raise ValidationError("json object key too long")
                stack.append((v, depth + 1))
            continue

        raise ValidationError(f"invalid json type: {type(node)}")
