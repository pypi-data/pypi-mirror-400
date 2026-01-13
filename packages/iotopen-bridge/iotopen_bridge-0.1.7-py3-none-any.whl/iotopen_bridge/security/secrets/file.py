# File: src/iotopen_bridge/security/secrets/file.py
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path


class FileSecrets:
    """Simple key=value secrets file reader.

    Lines:
      - empty lines ignored
      - comments start with '#'
      - values are returned as raw strings (trimmed)
    """

    def __init__(self, path: str) -> None:
        self._p = Path(path)

    def get(self, key: str) -> str | None:
        if not self._p.exists():
            return None

        for line in self._p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            k, v = line.split("=", 1)
            if k.strip() == key:
                return v.strip()

        return None
