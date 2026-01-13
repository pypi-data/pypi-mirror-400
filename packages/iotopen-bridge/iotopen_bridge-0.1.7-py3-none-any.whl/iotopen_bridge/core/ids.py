# File: src/iotopen_bridge/core/ids.py
# SPDX-License-Identifier: Apache-2.0

"""ID helpers for entity IDs, unique IDs and topic-safe identifiers.

Home Assistant entity_id rules are fairly strict (lowercase, digits, underscore).
The converter layer depends on these helpers to produce stable IDs.

Notes (relevant to MQTT discovery):
- Entity IDs (object_id) should only contain lowercase letters, numbers and underscores,
  and must not start or end with an underscore. HA enforces this in the UI and registry.
- `unique_id` must be stable per-entity; HA uses it for the entity registry.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass

_NON_ALNUM_UNDERSCORE = re.compile(r"[^a-z0-9_]+")
_MULTI_UNDERSCORE = re.compile(r"_+")


def sanitize_object_id(value: str, *, max_len: int = 255) -> str:
    """Convert arbitrary text into a HA-friendly object_id.

    Output:
    - lowercase
    - only [a-z0-9_]
    - no leading/trailing underscore
    - max length enforced
    """
    s = (value or "").strip().lower()
    s = s.replace(" ", "_").replace("-", "_")
    s = _NON_ALNUM_UNDERSCORE.sub("_", s)
    s = _MULTI_UNDERSCORE.sub("_", s).strip("_")

    if not s:
        s = "unnamed"

    if len(s) > max_len:
        s = s[:max_len].rstrip("_")

    return s


def _short_hash(value: str, n: int = 10) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:n]


def discovery_object_id_from_unique_id(unique_id: str, *, max_len: int = 64) -> str:
    """Derive a stable MQTT-discovery object_id from a unique_id.

    Home Assistant MQTT discovery topics have the form:
        <discovery_prefix>/<component>/[<node_id>/]<object_id>/config

    `object_id` should be stable and reasonably short. If the sanitized ID exceeds
    `max_len`, we keep a prefix and add a short hash suffix to preserve uniqueness.
    """
    uid = (unique_id or "").strip()
    # Make common separators topic-safe before sanitizing.
    base = uid.replace(":", "_").replace("/", "_").replace("\\", "_")
    slug = sanitize_object_id(base, max_len=max_len)

    if len(slug) <= max_len:
        return slug

    h = _short_hash(uid, 10)
    # room for "_" + hash
    keep = max_len - (len(h) + 1)
    if keep <= 0:
        return h

    prefix = slug[:keep].rstrip("_")
    if not prefix:
        return h
    return f"{prefix}_{h}"


def stable_device_id(installation_id: int, *, prefix: str = "iotopen") -> str:
    """Stable device identifier for HA device registry context."""
    return f"{prefix}_installation_{int(installation_id)}"


def stable_entity_name(friendly_name: str | None, fallback: str) -> str:
    """Prefer a provided friendly name; otherwise use a deterministic fallback."""
    n = (friendly_name or "").strip()
    return n if n else fallback


def new_uuid() -> str:
    """Random UUID4 hex string (32 chars)."""
    return uuid.uuid4().hex


@dataclass(frozen=True, slots=True)
class EntityId:
    """Represents a Home Assistant entity_id and a stable unique_id."""

    domain: str
    object_id: str

    @property
    def entity_id(self) -> str:
        return f"{self.domain}.{self.object_id}"

    def unique_id(self) -> str:
        return f"{self.domain}:{self.object_id}"
