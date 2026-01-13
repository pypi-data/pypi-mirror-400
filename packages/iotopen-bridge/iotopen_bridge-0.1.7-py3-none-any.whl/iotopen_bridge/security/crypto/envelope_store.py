# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/crypto/envelope_store.py
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from .nonce import is_valid_nonce


@dataclass(frozen=True, slots=True)
class NonceRecord:
    kid: str
    nonce: str
    seen_at: int
    expires_at: int


class EnvelopeNonceStore:
    """SQLite-backed replay protection store (kid+nonce with TTL).

    Low-risk design:
      - lives in its own table (doesn't modify existing schemas)
      - uses INSERT OR IGNORE to detect replays
      - periodic cleanup by expires_at
    """

    def __init__(self, db_path: str | Path) -> None:
        self._path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS crypto_nonces (
                    kid TEXT NOT NULL,
                    nonce TEXT NOT NULL,
                    seen_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    PRIMARY KEY (kid, nonce)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_crypto_nonces_expires ON crypto_nonces(expires_at);"
            )

    def cleanup(self, *, now_s: int | None = None) -> int:
        now = int(now_s if now_s is not None else time.time())
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM crypto_nonces WHERE expires_at <= ?", (now,))
            return int(cur.rowcount or 0)

    def nonce_seen(self, kid: str, nonce: str, ts: int, ttl_seconds: int) -> bool:
        """Return True if already seen (replay), else False and record it."""
        k = (kid or "default").strip() or "default"
        n = str(nonce or "")
        if not is_valid_nonce(n):
            # Treat invalid nonces as 'seen' so callers reject.
            return True

        seen_at = int(time.time())
        expires_at = int(max(seen_at, int(ts or 0)) + int(ttl_seconds))
        with self._connect() as conn:
            # opportunistic cleanup (cheap index-backed delete)
            conn.execute("DELETE FROM crypto_nonces WHERE expires_at <= ?", (seen_at,))

            cur = conn.execute(
                "INSERT OR IGNORE INTO crypto_nonces(kid, nonce, seen_at, expires_at) VALUES(?,?,?,?)",
                (k, n, seen_at, expires_at),
            )
            inserted = int(cur.rowcount or 0) == 1
            return not inserted
