# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/controllers/inventory.py
from __future__ import annotations

import contextlib
import hashlib
import json
import logging
import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from ..bridge.config import AuthzConfig
from ..core.event_bus import EventBus
from ..core.registry import InventoryDelta, Registry
from ..lynx.client import LynxApiClient
from ..models.events import InventoryEvent
from ..models.lynx import FunctionX
from ..models.persistence import InventorySnapshot
from ..security.authz.rules import AuthzRules
from ..storage.store import Store

_LOGGER = logging.getLogger(__name__)


def _stable_sha256(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            obj,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def _get_function_id(d: dict[str, Any]) -> int:
    for k in ("function_id", "functionId", "id"):
        v = d.get(k)
        if v is None or v == "":
            continue
        try:
            return int(v)
        except Exception:
            continue
    return 0


def _norm_topic(s: Any) -> str:
    t = str(s or "").strip()
    if t.startswith("/"):
        t = t[1:]
    return t


def _norm_prefix(s: Any) -> str:
    """Normalize topic-prefix strings.

    - strips whitespace
    - strips leading '/'
    - ensures it ends with '/' so matching stays segment-safe
    """
    p = str(s or "").strip()
    if p.startswith("/"):
        p = p[1:]
    if not p:
        return ""
    if not p.endswith("/"):
        p = p + "/"
    return p


def _prefix_match(topic: str, prefix: str) -> bool:
    """True if topic is under prefix using segment-boundary semantics."""
    t = _norm_topic(topic)
    p = _norm_prefix(prefix)
    if not t or not p:
        return False
    return t == p[:-1] or t.startswith(p)


@dataclass
class InventoryController:
    """Refresh inventory from Lynx and apply to Registry.

    Also optionally updates authz allowlists based on inventory so ENFORCE can work
    without manually listing every single upstream topic.

    Rules:
      - always allow exact topic_read (subscribe needs exact concrete topics)
      - allow exact topic_set only if it matches configured safe upstream prefixes
    """

    api: LynxApiClient
    registry: Registry

    bus: EventBus | None = None
    store: Store | None = None
    installation_id: int | None = None

    # Optional authz wiring (used by runtime)
    policy_rules: AuthzRules | None = None
    authz_cfg: AuthzConfig | None = None

    def refresh_sync(self) -> dict[str, Any]:
        if self.installation_id is None:
            raise ValueError("InventoryController.installation_id is required for refresh_sync()")
        return self.refresh(int(self.installation_id))

    def refresh(self, installation_id: int) -> dict[str, Any]:
        iid = int(installation_id)
        t0 = time.time()

        try:
            raw_list: list[dict[str, Any]] = list(self.api.list_functions(iid) or [])
        except Exception as e:
            _LOGGER.warning("Inventory refresh failed iid=%s err=%s", iid, e)
            return {
                "changed": False,
                "count": 0,
                "removed_function_ids": [],
                "removed_functions": [],
                "took_seconds": time.time() - t0,
                "error": str(e),
            }

        fxs: list[FunctionX] = []
        raw_norm: list[dict[str, Any]] = []
        for d in raw_list:
            if not isinstance(d, dict):
                continue
            try:
                fx = FunctionX.from_dict(d)
                if fx.function_id and int(fx.installation_id) == iid:
                    fxs.append(fx)
                    raw_norm.append(dict(d))
            except Exception:
                # One bad object must not poison the refresh
                continue

        sha = _stable_sha256(raw_norm)

        prev: InventorySnapshot | None = None
        snapshot_changed = True
        removed_from_prev: Sequence[dict[str, Any]] = ()
        if self.store is not None:
            try:
                prev = self.store.load_inventory(iid)
            except Exception:
                prev = None

        if prev is not None:
            snapshot_changed = prev.sha256 != sha
            prev_ids = {_get_function_id(d) for d in prev.functions}
            new_ids = {int(fx.function_id) for fx in fxs}
            removed_ids = prev_ids - new_ids
            if removed_ids:
                removed_from_prev = tuple(
                    d for d in prev.functions if _get_function_id(d) in removed_ids
                )

        # Apply to registry
        delta: InventoryDelta = self.registry.apply_inventory(iid, fxs)

        # Auto-allow discovered topics (if configured)
        self._update_authz_from_inventory(fxs)

        removed_functions: list[dict[str, Any]] = []
        if delta.removed_function_ids:
            for fid in delta.removed_function_ids:
                removed_functions.append({"installation_id": iid, "function_id": int(fid)})

        # Persist snapshot (best-effort)
        if self.store is not None:
            try:
                self.store.save_inventory(
                    InventorySnapshot(
                        installation_id=iid,
                        sha256=sha,
                        created_at=time.time(),
                        functions=raw_norm,
                    )
                )
            except Exception:
                _LOGGER.debug("Failed saving inventory snapshot", exc_info=True)

        changed = bool(delta.changed or snapshot_changed)

        # Publish event for runtime (GC + publish_all)
        if self.bus is not None:
            try:
                self.bus.publish(
                    InventoryEvent(
                        changed=changed,
                        function_count=len(fxs),
                        removed_functions=tuple(removed_from_prev)
                        if removed_from_prev
                        else tuple(removed_functions),
                    )
                )
            except Exception:
                _LOGGER.debug("Failed publishing InventoryEvent", exc_info=True)

        took = time.time() - t0
        _LOGGER.info(
            "Inventory refresh iid=%s count=%s changed=%s removed=%s took=%.3fs",
            iid,
            len(fxs),
            changed,
            len(removed_functions) if removed_functions else 0,
            took,
        )

        return {
            "changed": changed,
            "count": len(fxs),
            "removed_function_ids": list(delta.removed_function_ids),
            "removed_functions": removed_functions,
            "took_seconds": took,
        }

    def _update_authz_from_inventory(self, fxs: Sequence[FunctionX]) -> None:
        """Allow-list topic_read and (optionally) topic_set discovered in inventory."""
        if self.policy_rules is None or self.authz_cfg is None:
            return

        try:
            auto_allow_set = bool(getattr(self.authz_cfg, "auto_allow_topic_set", True))
            allow_set_prefixes = list(
                getattr(self.authz_cfg, "upstream_set_allow_prefixes", []) or []
            )
        except Exception:
            auto_allow_set = True
            allow_set_prefixes = ["obj/generated/", "obj/"]

        # topic_read: always allow exact topic
        for fx in fxs:
            tr = _norm_topic(getattr(fx, "topic_read", None))
            if tr:
                with contextlib.suppress(Exception):
                    self.policy_rules.allow_topic(tr)

        # topic_set: allow exact topics only if they match safe prefixes
        if not auto_allow_set:
            return

        for fx in fxs:
            ts = _norm_topic(getattr(fx, "topic_set", None))
            if not ts:
                continue

            ok = any(_prefix_match(ts, p) for p in allow_set_prefixes)
            if not ok:
                continue

            with contextlib.suppress(Exception):
                self.policy_rules.allow_topic(ts)
