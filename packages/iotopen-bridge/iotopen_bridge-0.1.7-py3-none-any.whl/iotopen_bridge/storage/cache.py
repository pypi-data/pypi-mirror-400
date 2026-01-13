# File: src/iotopen_bridge/storage/cache.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from ..models.persistence import DiscoverySnapshot, InventorySnapshot, LastSeen
from .store import Store


def _key(fid: int | None, iid: int | None) -> tuple[int, int]:
    return (int(fid or 0), int(iid or 0))


class CacheStore(Store):
    """In-memory write-through cache with optional persistence backend.

    - If backend is provided (e.g. SQLiteStore), this is a write-through cache.
    - If backend is None, this is a pure in-memory store (useful in tests).
    """

    def __init__(self, store: Store | None = None) -> None:
        self._backend = store
        self._inv: dict[int, InventorySnapshot] = {}
        self._disc: dict[str, DiscoverySnapshot] = {}
        self._last: dict[tuple[int, int], LastSeen] = {}

    # ---- inventory ----

    def save_inventory(self, snap: InventorySnapshot) -> None:
        iid = int(snap.installation_id)
        self._inv[iid] = snap
        if self._backend is not None:
            self._backend.save_inventory(snap)

    def load_inventory(self, installation_id: int) -> InventorySnapshot | None:
        iid = int(installation_id)
        cached = self._inv.get(iid)
        if cached is not None:
            return cached

        snap = self._backend.load_inventory(iid) if self._backend is not None else None
        if snap is not None:
            self._inv[iid] = snap
        return snap

    # ---- discovery ----

    def save_discovery(self, snap: DiscoverySnapshot) -> None:
        uid = str(snap.unique_id)
        self._disc[uid] = snap
        if self._backend is not None:
            self._backend.save_discovery(snap)

    def get_discovery(self, unique_id: str) -> DiscoverySnapshot | None:
        uid = str(unique_id)
        cached = self._disc.get(uid)
        if cached is not None:
            return cached

        snap = self._backend.get_discovery(uid) if self._backend is not None else None
        if snap is not None:
            self._disc[uid] = snap
        return snap

    # ---- last_seen ----

    def set_last_seen(self, last: LastSeen) -> None:
        k = _key(last.function_id, last.installation_id)
        self._last[k] = last
        if self._backend is not None:
            self._backend.set_last_seen(last)

    def get_last_seen(
        self, function_id: int, installation_id: int | None = None
    ) -> LastSeen | None:
        k = _key(function_id, installation_id)
        cached = self._last.get(k)
        if cached is not None:
            return cached

        snap = (
            self._backend.get_last_seen(int(function_id), installation_id)
            if self._backend is not None
            else None
        )
        if snap is not None:
            self._last[k] = snap
        return snap


# Backwards-compat: older code used CachedStore
CachedStore = CacheStore
