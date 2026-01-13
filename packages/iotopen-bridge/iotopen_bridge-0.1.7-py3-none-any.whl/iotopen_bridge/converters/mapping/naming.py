# File: src/iotopen_bridge/converters/mapping/naming.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

_SLUG_RE = re.compile(r"[^a-z0-9_]+")


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("-", "_").replace(" ", "_")
    s = _SLUG_RE.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "entity"


def _short_hash(s: str, n: int = 10) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:n]


def discovery_object_id_from_unique_id(unique_id: str, *, max_len: int = 64) -> str:
    """Derive a stable object_id from a unique_id.

    HA discovery topics use: <discovery_prefix>/<component>/[<node_id>/]<object_id>/config
    object_id must be stable. We also keep it reasonably short.
    """
    uid = (unique_id or "").strip()
    slug = _slugify(uid.replace(":", "_").replace("/", "_"))
    if len(slug) <= max_len:
        return slug
    h = _short_hash(uid, 10)
    keep = max_len - (len(h) + 1)
    return f"{slug[:keep]}_{h}"


def stable_device_id(installation_id: int, *, prefix: str = "iotopen") -> str:
    return f"{prefix}_installation_{int(installation_id)}"


def stable_entity_name(friendly_name: str | None, fallback: str) -> str:
    n = (friendly_name or "").strip()
    return n if n else fallback


@dataclass(frozen=True)
class Naming:
    unique_id: str
    object_id: str
    name: str
