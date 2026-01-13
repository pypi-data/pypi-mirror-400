# File: src/iotopen_bridge/core/registry.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import threading
import time
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any

from .errors import NotFoundError

"""In-memory registry for inventory + fast topic lookups."""


def _as_int(v: Any, default: int = 0) -> int:
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        return default


def _get_attr(obj: Any, name: str) -> Any:
    try:
        return getattr(obj, name)
    except Exception:
        return None


@dataclass(slots=True)
class InventoryDelta:
    changed: bool
    removed_function_ids: list[int]


class Registry:
    """Thread-safe inventory store with topic indexes.

    Enhancements:
      - Explicit mark_seen() helper for telemetry (single write path).
      - Collision-aware helpers: get_functions_by_topic_* so you can decide how to handle collisions.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()

        self.functions: dict[int, Any] = {}
        self._topic_read_index: dict[str, set[int]] = {}
        self._topic_set_index: dict[str, set[int]] = {}
        self._topic_collisions: set[str] = set()
        self.last_seen: dict[int, float] = {}

    # ---------- basics ----------

    def clear(self) -> None:
        with self._lock:
            self.functions.clear()
            self._topic_read_index.clear()
            self._topic_set_index.clear()
            self._topic_collisions.clear()
            self.last_seen.clear()

    def iter_functions(self) -> Iterator[Any]:
        with self._lock:
            values = list(self.functions.values())
        return iter(values)

    def get_function(self, function_id: int) -> Any | None:
        with self._lock:
            return self.functions.get(int(function_id))

    def require_function(self, function_id: int) -> Any:
        fx = self.get_function(function_id)
        if fx is None:
            raise NotFoundError(f"Function not found: {function_id}")
        return fx

    def mark_seen(self, function_id: int, ts: float | None = None) -> None:
        fid = int(function_id)
        with self._lock:
            self.last_seen[fid] = float(ts if ts is not None else time.time())

    # ---------- compatibility ----------

    def replace_functions(self, functions: Iterable[Any]) -> InventoryDelta:
        """Backward-compatible wrapper."""
        items = list(functions)
        inferred_iid = 0
        for fx in items:
            inferred_iid = _as_int(_get_attr(fx, "installation_id"), 0)
            if inferred_iid:
                break

        if inferred_iid:
            return self.apply_inventory(inferred_iid, items)

        self.clear()
        changed = self.upsert_functions(items)
        return InventoryDelta(changed=changed, removed_function_ids=[])

    # ---------- topic lookups ----------

    def get_function_by_topic_read(self, topic: str) -> Any | None:
        """Returns a single function only if non-colliding."""
        topic = (topic or "").strip()
        with self._lock:
            ids = self._topic_read_index.get(topic)
            if not ids or len(ids) != 1:
                return None
            fid = next(iter(ids))
            return self.functions.get(fid)

    def get_function_by_topic_set(self, topic: str) -> Any | None:
        """Returns a single function only if non-colliding."""
        topic = (topic or "").strip()
        with self._lock:
            ids = self._topic_set_index.get(topic)
            if not ids or len(ids) != 1:
                return None
            fid = next(iter(ids))
            return self.functions.get(fid)

    def get_functions_by_topic_read(self, topic: str) -> list[Any]:
        """Returns all functions matching topic (collision-aware)."""
        topic = (topic or "").strip()
        with self._lock:
            ids = list(self._topic_read_index.get(topic, set()))
            return [self.functions[i] for i in ids if i in self.functions]

    def get_functions_by_topic_set(self, topic: str) -> list[Any]:
        """Returns all functions matching topic (collision-aware)."""
        topic = (topic or "").strip()
        with self._lock:
            ids = list(self._topic_set_index.get(topic, set()))
            return [self.functions[i] for i in ids if i in self.functions]

    def get_function_ids_by_topic_read(self, topic: str) -> set[int]:
        topic = (topic or "").strip()
        with self._lock:
            return set(self._topic_read_index.get(topic, set()))

    def get_function_ids_by_topic_set(self, topic: str) -> set[int]:
        topic = (topic or "").strip()
        with self._lock:
            return set(self._topic_set_index.get(topic, set()))

    def topic_collisions(self) -> set[str]:
        with self._lock:
            return set(self._topic_collisions)

    # ---------- indexing ----------

    def rebuild_indexes(self) -> None:
        with self._lock:
            self._topic_read_index.clear()
            self._topic_set_index.clear()
            self._topic_collisions.clear()

            for fid, fx in self.functions.items():
                self._index_one(fid, fx)

    def _index_one(self, fid: int, fx: Any) -> None:
        tr = _get_attr(fx, "topic_read")
        ts = _get_attr(fx, "topic_set")
        if isinstance(tr, str) and tr.strip():
            tr = tr.strip()
            s = self._topic_read_index.setdefault(tr, set())
            s.add(fid)
            if len(s) > 1:
                self._topic_collisions.add(tr)
        if isinstance(ts, str) and ts.strip():
            ts = ts.strip()
            s = self._topic_set_index.setdefault(ts, set())
            s.add(fid)
            if len(s) > 1:
                self._topic_collisions.add(ts)

    def _unindex_one(self, fid: int, fx: Any) -> None:
        tr = _get_attr(fx, "topic_read")
        ts = _get_attr(fx, "topic_set")
        if isinstance(tr, str) and tr.strip():
            tr = tr.strip()
            s = self._topic_read_index.get(tr)
            if s:
                s.discard(fid)
                if not s:
                    self._topic_read_index.pop(tr, None)
                if len(s) <= 1:
                    self._topic_collisions.discard(tr)
        if isinstance(ts, str) and ts.strip():
            ts = ts.strip()
            s = self._topic_set_index.get(ts)
            if s:
                s.discard(fid)
                if not s:
                    self._topic_set_index.pop(ts, None)
                if len(s) <= 1:
                    self._topic_collisions.discard(ts)

    # ---------- mutation ----------

    def upsert_function(self, fx: Any) -> bool:
        fid = _as_int(_get_attr(fx, "function_id"), 0)
        if not fid:
            return False

        with self._lock:
            prev = self.functions.get(fid)
            changed = prev is None
            if prev is not None:
                try:
                    changed = prev != fx
                except Exception:
                    changed = prev is not fx
                if changed:
                    self._unindex_one(fid, prev)

            self.functions[fid] = fx
            self._index_one(fid, fx)

        return changed

    def upsert_functions(self, functions: Iterable[Any]) -> bool:
        changed = False
        for fx in functions:
            if self.upsert_function(fx):
                changed = True
        return changed

    def remove_functions(self, function_ids: Iterable[int]) -> None:
        with self._lock:
            for fid0 in function_ids:
                fid = int(fid0)
                fx = self.functions.pop(fid, None)
                self.last_seen.pop(fid, None)
                if fx is not None:
                    self._unindex_one(fid, fx)

    def apply_inventory(self, installation_id: int, functions: Iterable[Any]) -> InventoryDelta:
        iid = int(installation_id)

        new_items = list(functions)
        new_ids: set[int] = set()
        for fx in new_items:
            if _as_int(_get_attr(fx, "installation_id"), 0) != iid:
                continue
            fid = _as_int(_get_attr(fx, "function_id"), 0)
            if fid:
                new_ids.add(fid)

        with self._lock:
            old_ids = {
                fid
                for fid, fx in self.functions.items()
                if _as_int(_get_attr(fx, "installation_id"), 0) == iid
            }

        removed = sorted(old_ids - new_ids)
        changed = bool(removed)

        if removed:
            self.remove_functions(removed)

        if self.upsert_functions(new_items):
            changed = True

        return InventoryDelta(changed=changed, removed_function_ids=removed)
