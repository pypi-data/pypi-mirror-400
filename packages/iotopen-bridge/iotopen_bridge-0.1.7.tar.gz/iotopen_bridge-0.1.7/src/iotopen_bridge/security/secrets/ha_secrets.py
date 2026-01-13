# File: src/iotopen_bridge/security/secrets/ha_secrets.py
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import yaml


class HASecrets:
    """Read Home Assistant-style secrets.yaml and expose get(key)."""

    def __init__(self, path: str) -> None:
        self._p = Path(path)

    def get(self, key: str) -> str | None:
        if not self._p.exists():
            return None

        data = yaml.safe_load(self._p.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            return None

        v = data.get(key)
        if v is None:
            return None
        return str(v)
