# File: src/iotopen_bridge/controllers/reconciliation.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import Any

from ..core.registry import Registry


@dataclass
class ReconciliationController:
    """Sanity checks + diagnostics for registry/topic indexes.

    Enhancements:
      - provides operator-grade report()
      - optional strict mode (assert_healthy)
      - uses existing Registry APIs (topic_collisions / rebuild_indexes / iter_functions)
    """

    registry: Registry

    def report(self) -> dict[str, Any]:
        # ensure indexes are current if method exists
        if hasattr(self.registry, "rebuild_indexes"):
            with contextlib.suppress(Exception):
                self.registry.rebuild_indexes()

        collisions: set[str] = set()
        if hasattr(self.registry, "topic_collisions"):
            try:
                collisions = set(self.registry.topic_collisions())
            except Exception:
                collisions = set()

        missing_topic_read: list[int] = []
        missing_installation: list[int] = []

        try:
            it = (
                self.registry.iter_functions()
                if hasattr(self.registry, "iter_functions")
                else iter(self.registry.functions.values())
            )
        except Exception:
            it = iter([])

        for fx in it:
            fid = int(getattr(fx, "function_id", 0) or 0)
            iid = int(getattr(fx, "installation_id", 0) or 0)
            tr = getattr(fx, "topic_read", None)

            if not iid:
                missing_installation.append(fid)
            if not isinstance(tr, str) or not tr.strip():
                missing_topic_read.append(fid)

        return {
            "function_count": len(getattr(self.registry, "functions", {}) or {}),
            "topic_collisions": sorted(collisions),
            "missing_topic_read": sorted(set(missing_topic_read)),
            "missing_installation_id": sorted(set(missing_installation)),
        }

    def assert_healthy(self) -> None:
        r = self.report()
        if r["topic_collisions"]:
            raise RuntimeError(f"Topic collisions detected: {r['topic_collisions']}")
        if r["missing_topic_read"]:
            raise RuntimeError(f"Functions missing topic_read: {r['missing_topic_read']}")
