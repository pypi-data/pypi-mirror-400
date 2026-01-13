# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/storage/store.py
from __future__ import annotations

import contextlib
import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..models.persistence import DiscoverySnapshot, InventorySnapshot, LastSeen


class Store:
    def get_discovery(self, unique_id: str) -> DiscoverySnapshot | None:
        raise NotImplementedError

    def save_discovery(self, snap: DiscoverySnapshot) -> None:
        raise NotImplementedError

    def load_inventory(self, installation_id: int) -> InventorySnapshot | None:
        raise NotImplementedError

    def save_inventory(self, snap: InventorySnapshot) -> None:
        raise NotImplementedError

    def set_last_seen(self, last: LastSeen) -> None:
        raise NotImplementedError

    def get_last_seen(
        self, function_id: int, installation_id: int | None = None
    ) -> LastSeen | None:
        raise NotImplementedError


class _Local(threading.local):
    conn: sqlite3.Connection | None = None


@dataclass
class SqliteStore(Store):
    """SQLite store with thread-local connection reuse."""

    path: str
    _schema_lock: threading.RLock = field(
        default_factory=threading.RLock, init=False, repr=False, compare=False
    )
    _local: _Local = field(default_factory=_Local, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def close(self) -> None:
        if self._local.conn is not None:
            with contextlib.suppress(Exception):
                self._local.conn.close()
            self._local.conn = None

    def _connect(self) -> sqlite3.Connection:
        if self._local.conn is not None:
            return self._local.conn

        conn = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA temp_store=MEMORY;")
        conn.execute("PRAGMA foreign_keys=ON;")

        self._local.conn = conn
        return conn

    def _init_db(self) -> None:
        with self._schema_lock:
            conn = self._connect()

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS discovery_snapshot (
                    unique_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_discovery_topic ON discovery_snapshot(topic);"
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory_snapshot (
                    installation_id INTEGER PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    functions_json TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def get_discovery(self, unique_id: str) -> DiscoverySnapshot | None:
        uid = str(unique_id)
        conn = self._connect()
        cur = conn.execute(
            "SELECT unique_id, topic, payload_sha256, created_at FROM discovery_snapshot WHERE unique_id=?",
            (uid,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return DiscoverySnapshot(
            unique_id=str(row["unique_id"]),
            topic=str(row["topic"]),
            payload_sha256=str(row["payload_sha256"]),
            created_at=float(row["created_at"]),
        )

    def save_discovery(self, snap: DiscoverySnapshot) -> None:
        conn = self._connect()
        created = float(snap.created_at or time.time())
        conn.execute(
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
        conn.commit()

    def load_inventory(self, installation_id: int) -> InventorySnapshot | None:
        iid = int(installation_id)
        conn = self._connect()
        cur = conn.execute(
            "SELECT installation_id, sha256, created_at, functions_json FROM inventory_snapshot WHERE installation_id=?",
            (iid,),
        )
        row = cur.fetchone()
        if not row:
            return None

        functions: list[dict[str, Any]]
        try:
            functions_obj = json.loads(str(row["functions_json"]) or "[]")
            functions = functions_obj if isinstance(functions_obj, list) else []
        except Exception:
            functions = []

        # Ensure element type is dict[str, Any]
        functions = [x for x in functions if isinstance(x, dict)]

        return InventorySnapshot(
            installation_id=int(row["installation_id"]),
            sha256=str(row["sha256"]),
            created_at=float(row["created_at"]),
            functions=functions,
        )

    def save_inventory(self, snap: InventorySnapshot) -> None:
        conn = self._connect()
        created = float(snap.created_at or time.time())
        functions_json = json.dumps(
            snap.functions or [], ensure_ascii=False, separators=(",", ":"), sort_keys=True
        )

        conn.execute(
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
        conn.commit()
