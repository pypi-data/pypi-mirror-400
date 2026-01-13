# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/validation/limits.py
from __future__ import annotations

from dataclasses import dataclass

from ...core.errors import ValidationError


@dataclass(frozen=True)
class Limits:
    """Defensive limits for payload decoding and MQTT topic handling."""

    # MQTT payload safety
    max_payload_bytes: int = 256_000

    # MQTT topic safety (string length)
    max_topic_length: int = 512
    max_topic_filter_length: int = 512

    # JSON safety
    max_json_depth: int = 32
    max_json_keys: int = 10_000
    max_json_array_len: int = 50_000
    max_json_total_items: int = 200_000
    max_string_chars: int = 200_000


BytesLike = bytes | bytearray | memoryview


def enforce_payload(payload: BytesLike | str, limits: Limits) -> bytes:
    """Normalize payload to bytes and enforce max size."""
    if payload is None:
        raise ValidationError("payload is None")

    if isinstance(payload, str):
        b = payload.encode("utf-8")
    elif isinstance(payload, (bytes, bytearray)):
        b = bytes(payload)
    elif isinstance(payload, memoryview):
        b = payload.tobytes()
    else:
        raise ValidationError(
            f"payload must be bytes/bytearray/memoryview/str, got {type(payload)}"
        )

    if len(b) > int(limits.max_payload_bytes):
        raise ValidationError(f"payload too large: {len(b)} > {limits.max_payload_bytes}")
    return b


def enforce_topic(topic: str, limits: Limits) -> str:
    """Enforce max topic length."""
    t = str(topic or "")
    if not t:
        raise ValidationError("topic is empty")
    if len(t) > int(limits.max_topic_length):
        raise ValidationError(f"topic too long: {len(t)} > {limits.max_topic_length}")
    return t


def enforce_topic_filter(topic_filter: str, limits: Limits) -> str:
    """Enforce max topic filter length."""
    tf = str(topic_filter or "")
    if not tf:
        raise ValidationError("topic_filter is empty")
    if len(tf) > int(limits.max_topic_filter_length):
        raise ValidationError(
            f"topic_filter too long: {len(tf)} > {limits.max_topic_filter_length}"
        )
    return tf
