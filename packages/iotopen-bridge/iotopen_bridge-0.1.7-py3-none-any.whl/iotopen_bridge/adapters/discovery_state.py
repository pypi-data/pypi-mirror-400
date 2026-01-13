# File: src/iotopen_bridge/adapters/discovery_state.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..models.persistence import DiscoverySnapshot
from ..storage.store import Store

PublishFn = Callable[[str, str | bytes, int, bool], None]


def _sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _stable_json_dumps(obj: Any) -> str:
    # Stable + compact: guarantees consistent hashing across runs/platforms.
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class DiscoveryDecision:
    """Return value for upserts (useful for observability and tests)."""

    published: bool
    payload_json: str
    payload_sha256: str
    old_topic_cleared: bool


@dataclass
class DiscoveryState:
    """Owns discovery hashing, idempotency, and retained-topic migration cleanup."""

    store: Store
    publish: PublishFn
    qos: int = 1
    retain: bool = True

    @property
    def empty_hash(self) -> str:
        return _sha256_text("")

    def get(self, unique_id: str) -> DiscoverySnapshot | None:
        try:
            return self.store.get_discovery(unique_id)
        except Exception:
            return None

    def _clear_retained(self, topic: str) -> bool:
        try:
            self.publish(topic, "", int(self.qos), True)
            return True
        except Exception:
            return False

    def save(self, snap: DiscoverySnapshot) -> None:
        # Best-effort persistence by design
        with contextlib.suppress(Exception):
            self.store.save_discovery(snap)

    def upsert(
        self,
        *,
        unique_id: str,
        topic: str,
        payload_obj: Any,
        now: float | None = None,
    ) -> DiscoveryDecision:
        """Idempotent publish of discovery config.

        Behavior:
          - Computes stable JSON + sha256
          - If topic changed: clears old retained topic (if old snapshot wasn't already empty)
          - Publishes only when (topic, hash) differs from last snapshot
          - Persists the new snapshot (best-effort)
        """
        ts = float(time.time() if now is None else now)

        payload_json = _stable_json_dumps(payload_obj)
        payload_hash = _sha256_text(payload_json)

        prev = self.get(unique_id)

        old_topic_cleared = False
        if (
            prev is not None
            and prev.topic
            and prev.topic != topic
            and prev.payload_sha256 != self.empty_hash
        ):
            old_topic_cleared = self._clear_retained(prev.topic)

        if prev is not None and prev.topic == topic and prev.payload_sha256 == payload_hash:
            return DiscoveryDecision(
                published=False,
                payload_json=payload_json,
                payload_sha256=payload_hash,
                old_topic_cleared=old_topic_cleared,
            )

        # Publish retained discovery config
        self.publish(topic, payload_json, int(self.qos), bool(self.retain))

        # Persist snapshot (best-effort)
        self.save(
            DiscoverySnapshot(
                unique_id=unique_id,
                topic=topic,
                payload_sha256=payload_hash,
                created_at=ts,
                schema_version=1,
            )
        )

        return DiscoveryDecision(
            published=True,
            payload_json=payload_json,
            payload_sha256=payload_hash,
            old_topic_cleared=old_topic_cleared,
        )

    def mark_deleted(
        self,
        *,
        unique_id: str,
        topic: str,
        now: float | None = None,
    ) -> bool:
        """Clear retained discovery config and persist an 'empty' snapshot."""
        ts = float(time.time() if now is None else now)

        self._clear_retained(topic)

        self.save(
            DiscoverySnapshot(
                unique_id=unique_id,
                topic=topic,
                payload_sha256=self.empty_hash,
                created_at=ts,
                schema_version=1,
            )
        )
        return True
