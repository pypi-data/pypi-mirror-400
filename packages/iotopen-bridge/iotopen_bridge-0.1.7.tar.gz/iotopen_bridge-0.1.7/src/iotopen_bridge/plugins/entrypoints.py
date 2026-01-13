# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/plugins/entrypoints.py
from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any


def load_entrypoint_group(group: str) -> list[Any]:
    """
    Load all entry points under a group and return the loaded objects.

    Python >= 3.10 returns an EntryPoints object with `.select(group=...)`.
    Since this project targets Python >= 3.10, we use that API directly.
    """
    eps = entry_points()
    group_eps = eps.select(group=str(group))

    out: list[Any] = []
    for ep in group_eps:
        try:
            out.append(ep.load())
        except Exception:
            # Best-effort plugin loading: ignore broken plugins.
            continue
    return out
