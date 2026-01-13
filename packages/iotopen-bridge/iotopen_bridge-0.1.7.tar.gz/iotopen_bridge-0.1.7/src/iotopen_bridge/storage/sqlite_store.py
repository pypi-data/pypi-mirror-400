# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/storage/sqlite_store.py
from __future__ import annotations

import contextlib
import json
import sqlite3
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from ..core.errors import StorageError
from ..models.persistence import DiscoverySnapshot, InventorySnapshot, LastSeen
from .store import Store


def _iid_norm(iid: int | None) -> int:
    # Use 0 to represent "no installation scope"
    return int(iid or 0)


class SQLiteStore(Store):
    """SQLite persistence backend.

    Tables:
      - inventory_snapshot: latest inventory snapshot per installation_id
      - discovery_snapshot: last discovery payload hash per unique_id
      - last_seen: key -> last_seen_at (+ optional value_preview)

    Notes:
      - Explicitly closes connections to reduce Windows file-handle locking issues.
      - Uses WAL for better concurrency (readers don't block writers).
    """

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._init_lock = threading.RLock()
        self._init()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        try:
            conn = sqlite3.connect(str(self.path), timeout=30, check_same_thread=False)
            conn.row_factory = sqlite3.Row

            # Pragmas (best-effort)
            with contextlib.suppress(Exception):
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("PRAGMA foreign_keys=ON;")

            yield conn
        except sqlite3.Error as e:
            raise StorageError(str(e)) from e
        finally:
            with contextlib.suppress(Exception):
                conn.close()  # type: ignore[unbound-local]

    def _init(self) -> None:
        with self._init_lock, self._connect() as c:
            c.execute(
                """
                    CREATE TABLE IF NOT EXISTS inventory_snapshot (
                        installation_id INTEGER PRIMARY KEY,
                        sha256 TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        functions_json TEXT NOT NULL
                    );
                    """
            )
            c.execute(
                """
                    CREATE TABLE IF NOT EXISTS discovery_snapshot (
                        unique_id TEXT PRIMARY KEY,
                        topic TEXT NOT NULL,
                        payload_sha256 TEXT NOT NULL,
                        created_at REAL NOT NULL
                    );
                    """
            )
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_discovery_topic ON discovery_snapshot(topic);"
            )

            # ✅ Key-based last_seen (matches unit test: LastSeen("k", ts, "v"))
            c.execute(
                """
                    CREATE TABLE IF NOT EXISTS last_seen (
                        key TEXT PRIMARY KEY,
                        last_seen_at REAL NOT NULL,
                        value_preview TEXT
                    );
                    """
            )
            c.commit()

    # -------- inventory --------

    def save_inventory(self, snap: InventorySnapshot) -> None:
        created = float(snap.created_at or time.time())
        functions_json = json.dumps(
            snap.functions or [],
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            default=str,
        )

        with self._connect() as c:
            c.execute(
                """
                INSERT INTO inventory_snapshot(installation_id, sha256, created_at, functions_json)
                VALUES(?,?,?,?)
                ON CONFLICT(installation_id) DO UPDATE SET
                    sha256=excluded.sha256,
                    created_at=excluded.created_at,
                    functions_json=excluded.functions_json
                """,
                (int(snap.installation_id), str(snap.sha256), created, functions_json),
            )
            c.commit()

    def load_inventory(self, installation_id: int) -> InventorySnapshot | None:
        iid = int(installation_id)
        with self._connect() as c:
            row = c.execute(
                """
                SELECT installation_id, sha256, created_at, functions_json
                FROM inventory_snapshot
                WHERE installation_id=?
                """,
                (iid,),
            ).fetchone()

        if not row:
            return None

        try:
            functions = json.loads(str(row["functions_json"]) or "[]")
            if not isinstance(functions, list):
                functions = []
        except Exception:
            functions = []

        return InventorySnapshot(
            installation_id=int(row["installation_id"]),
            sha256=str(row["sha256"]),
            created_at=float(row["created_at"]),
            functions=functions,
        )

    # -------- discovery --------

    def save_discovery(self, snap: DiscoverySnapshot) -> None:
        created = float(snap.created_at or time.time())
        with self._connect() as c:
            c.execute(
                """
                INSERT INTO discovery_snapshot(unique_id, topic, payload_sha256, created_at)
                VALUES(?,?,?,?)
                ON CONFLICT(unique_id) DO UPDATE SET
                    topic=excluded.topic,
                    payload_sha256=excluded.payload_sha256,
                    created_at=excluded.created_at
                """,
                (str(snap.unique_id), str(snap.topic), str(snap.payload_sha256), created),
            )
            c.commit()

    def get_discovery(self, unique_id: str) -> DiscoverySnapshot | None:
        uid = str(unique_id)
        with self._connect() as c:
            row = c.execute(
                """
                SELECT unique_id, topic, payload_sha256, created_at
                FROM discovery_snapshot
                WHERE unique_id=?
                """,
                (uid,),
            ).fetchone()

        if not row:
            return None

        return DiscoverySnapshot(
            unique_id=str(row["unique_id"]),
            topic=str(row["topic"]),
            payload_sha256=str(row["payload_sha256"]),
            created_at=float(row["created_at"]),
        )

    # -------- last_seen --------

    def set_last_seen(self, last: LastSeen) -> None:
        key = str(getattr(last, "key", "") or "").strip()

        # Backwards compat: if key missing, derive from iid/fid when available
        if not key:
            iid = getattr(last, "installation_id", None)
            fid = getattr(last, "function_id", None)
            if iid is None or fid is None:
                raise StorageError("LastSeen.key is required (or installation_id+function_id)")
            key = f"{_iid_norm(iid)}:{int(fid)}"

        ts = float(getattr(last, "last_seen_at", time.time()))
        preview = getattr(last, "value_preview", None)
        preview_s = None if preview is None else str(preview)

        with self._connect() as c:
            c.execute(
                """
                INSERT INTO last_seen(key, last_seen_at, value_preview)
                VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET
                    last_seen_at=excluded.last_seen_at,
                    value_preview=excluded.value_preview
                """,
                (key, ts, preview_s),
            )
            c.commit()

    def get_last_seen(
        self, key_or_function_id: int | str, installation_id: int | None = None
    ) -> LastSeen | None:
        # Support old-style: get_last_seen(function_id, installation_id=...)
        if isinstance(key_or_function_id, int):
            iid = _iid_norm(installation_id)
            key = f"{iid}:{int(key_or_function_id)}"
        else:
            key = str(key_or_function_id)

            # If numeric string + installation_id provided, treat like old style too
            if installation_id is not None:
                with contextlib.suppress(Exception):
                    fid = int(key)
                    iid = _iid_norm(installation_id)
                    key = f"{iid}:{fid}"

        with self._connect() as c:
            row = c.execute(
                """
                SELECT key, last_seen_at, value_preview
                FROM last_seen
                WHERE key=?
                """,
                (key,),
            ).fetchone()

        if not row:
            return None

        # Parse optional iid:fid
        inst: int | None = None
        fid2: int | None = None
        k = str(row["key"])
        if ":" in k:
            left, right = k.split(":", 1)
            try:
                inst = int(left)
                fid2 = int(right)
                if inst == 0:
                    inst = None
            except Exception:
                inst = None
                fid2 = None

        return LastSeen(
            key=k,
            last_seen_at=float(row["last_seen_at"]),
            value_preview=(None if row["value_preview"] is None else str(row["value_preview"])),
            installation_id=inst,
            function_id=fid2,
        )
