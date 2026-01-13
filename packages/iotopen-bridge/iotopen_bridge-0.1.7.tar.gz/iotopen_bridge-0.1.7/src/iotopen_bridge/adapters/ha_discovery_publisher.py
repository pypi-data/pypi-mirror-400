# File: src/iotopen_bridge/adapters/ha_discovery_publisher.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from ..adapters.discovery_state import DiscoveryState, PublishFn
from ..converters.ha_discovery.builder import build_discovery
from ..converters.mapping.function_to_entity import function_to_entity
from ..converters.mapping.ha_props import infer_semantics
from ..converters.mapping.naming import discovery_object_id_from_unique_id
from ..core.mapping_registry import MappingRegistry
from ..core.registry import Registry
from ..models.lynx import FunctionX
from ..models.persistence import DiscoverySnapshot
from ..storage.store import Store


def _get_int(d: dict[str, Any], *keys: str, default: int = 0) -> int:
    for k in keys:
        if k in d:
            try:
                return int(d[k] or 0)
            except Exception:
                return default
    return default


@dataclass
class HADiscoveryPublisher:
    """Home Assistant MQTT discovery publisher.

    - Discovery config topics are typically retained; we publish retain=True.
    - To remove stale retained discovery configs, publish an empty retained payload on the old topic.

    Note: This publisher targets the *downstream* (Home Assistant) MQTT broker.
    """

    registry: Registry
    store: Store
    discovery_prefix: str
    state_prefix: str
    publish: PublishFn
    bridge_availability_topic: str
    attributes_enabled: bool
    per_entity_availability: bool

    mapping: MappingRegistry | None = None

    discovery_qos: int = 1
    discovery_retain: bool = True

    def _availability_topic(self, installation_id: int, function_id: int) -> str:
        return f"{self.state_prefix}/{installation_id}/{function_id}/availability"

    def _state_topic(self, installation_id: int, function_id: int) -> str:
        return f"{self.state_prefix}/{installation_id}/{function_id}/state"

    def _attributes_topic(self, installation_id: int, function_id: int) -> str:
        return f"{self.state_prefix}/{installation_id}/{function_id}/attributes"

    def _unique_id(self, installation_id: int, function_id: int) -> str:
        return f"iotopen:{installation_id}:{function_id}"

    @property
    def _state(self) -> DiscoveryState:
        return DiscoveryState(
            store=self.store,
            publish=self.publish,
            qos=int(self.discovery_qos),
            retain=bool(self.discovery_retain),
        )

    def publish_all(self) -> int:
        published = 0
        state = self._state

        for fx in self.registry.iter_functions():
            if not getattr(fx, "installation_id", None) or not getattr(fx, "function_id", None):
                continue

            installation_id = int(fx.installation_id)
            function_id = int(fx.function_id)
            uid = self._unique_id(installation_id, function_id)

            availability_topics: list[str] = []
            if self.bridge_availability_topic:
                availability_topics.append(self.bridge_availability_topic)
            if self.per_entity_availability:
                availability_topics.append(self._availability_topic(installation_id, function_id))

            entity = function_to_entity(
                fx,
                ha_state_prefix=self.state_prefix,
                mapping=self.mapping,
                availability_topics=availability_topics,
                availability_mode="all",
                attributes_enabled=bool(self.attributes_enabled),
                expire_after_seconds=None,
            )
            disc = build_discovery(entity, discovery_prefix=self.discovery_prefix)

            decision = state.upsert(unique_id=uid, topic=disc.topic, payload_obj=disc.payload)
            if decision.published:
                published += 1

        return published

    def garbage_collect(self, removed_functions: Sequence[dict[str, Any]]) -> int:
        removed_count = 0
        state = self._state
        empty_hash = state.empty_hash

        for d in removed_functions:
            installation_id = _get_int(d, "installation_id", "installationId", default=0)
            function_id = _get_int(d, "function_id", "functionId", "id", default=0)
            fx_type = str(d.get("type") or "")

            if not installation_id or not function_id:
                continue

            uid = self._unique_id(installation_id, function_id)

            # Load previous snapshot (best-effort)
            prev: DiscoverySnapshot | None
            try:
                prev = self.store.get_discovery(uid)
            except Exception:
                prev = None

            if prev is None or prev.payload_sha256 == empty_hash:
                continue

            discovery_topic: str | None = prev.topic or None
            if not discovery_topic:
                component: str | None
                try:
                    fx_obj = FunctionX.from_dict(d)
                    component = infer_semantics(fx_obj).component
                except Exception:
                    component = None

                if not component:
                    ftl = fx_type.lower()
                    if ftl == "switch":
                        component = "switch"
                    elif ftl.startswith(("binary", "alarm", "contact", "door", "window")):
                        component = "binary_sensor"
                    else:
                        component = "sensor"

                object_id = discovery_object_id_from_unique_id(uid)
                discovery_topic = f"{self.discovery_prefix}/{component}/{object_id}/config"

            # Clear retained discovery config + persist empty snapshot
            state.mark_deleted(unique_id=uid, topic=str(discovery_topic))
            removed_count += 1

            # Optional cleanup: clearing retained aux topics avoids stale UI if you ever retain them.
            with contextlib.suppress(Exception):
                self.publish(self._state_topic(installation_id, function_id), "", 1, True)

            if self.attributes_enabled:
                with contextlib.suppress(Exception):
                    self.publish(self._attributes_topic(installation_id, function_id), "", 1, True)

            if self.per_entity_availability:
                with contextlib.suppress(Exception):
                    self.publish(
                        self._availability_topic(installation_id, function_id), "", 1, True
                    )

        return removed_count

    def publish_bridge_availability(
        self, online: bool, *, qos: int = 1, retain: bool = True
    ) -> None:
        if not self.bridge_availability_topic:
            return
        self.publish(self.bridge_availability_topic, "online" if online else "offline", qos, retain)

    def publish_entity_availability(
        self, installation_id: int, function_id: int, online: bool
    ) -> None:
        if not self.per_entity_availability:
            return
        self.publish(
            self._availability_topic(int(installation_id), int(function_id)),
            "online" if online else "offline",
            1,
            True,
        )

    def publish_attributes(
        self,
        installation_id: int,
        function_id: int,
        attrs: dict[str, Any],
        qos: int,
        retain: bool,
    ) -> None:
        if not self.attributes_enabled:
            return

        # Keep payload stable and compact (same format as DiscoveryState).
        payload = json.dumps(attrs or {}, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        self.publish(
            self._attributes_topic(int(installation_id), int(function_id)), payload, qos, retain
        )
