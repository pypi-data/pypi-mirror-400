# File: src/iotopen_bridge/models/persistence.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DiscoverySnapshot:
    unique_id: str
    topic: str
    payload_sha256: str
    created_at: float
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": int(self.schema_version),
            "unique_id": self.unique_id,
            "topic": self.topic,
            "payload_sha256": self.payload_sha256,
            "created_at": float(self.created_at),
        }


@dataclass(frozen=True, slots=True)
class InventorySnapshot:
    installation_id: int
    sha256: str
    created_at: float
    functions: list[dict[str, Any]]
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": int(self.schema_version),
            "installation_id": int(self.installation_id),
            "sha256": self.sha256,
            "created_at": float(self.created_at),
            "functions": list(self.functions),
        }


@dataclass(frozen=True, slots=True)
class LastSeen:
    """Persisted last-seen timestamp.

    Unit test expects positional ctor: LastSeen("k", ts, "v")
    Runtime can optionally also store per-function identity via installation_id/function_id.
    """

    key: str
    last_seen_at: float
    value_preview: str | None = None

    installation_id: int | None = None
    function_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "key": self.key,
            "last_seen_at": float(self.last_seen_at),
            "value_preview": self.value_preview,
            "installation_id": self.installation_id,
            "function_id": self.function_id,
        }
        return {k: v for k, v in d.items() if v is not None}
