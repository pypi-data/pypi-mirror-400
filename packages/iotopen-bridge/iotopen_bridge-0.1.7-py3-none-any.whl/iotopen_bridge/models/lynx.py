# File: src/iotopen_bridge/models/lynx.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _get_any(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in d and d.get(k) is not None:
            return d.get(k)
    return default


def _as_int(v: Any, default: int = 0) -> int:
    try:
        if v is None:
            return default
        return int(v)
    except Exception:
        return default


def _as_str(v: Any, default: str = "") -> str:
    if v is None:
        return default
    try:
        return str(v)
    except Exception:
        return default


@dataclass(frozen=True, slots=True)
class FunctionX:
    """Normalized FunctionX model (permissive parsing; upstream may evolve fields)."""

    function_id: int
    installation_id: int
    type: str
    topic_read: str

    topic_set: str | None = None
    friendly_name: str | None = None
    device_id: int | None = None

    state_on: Any | None = None
    state_off: Any | None = None

    # Optional extra metadata (ignored by current bridge logic but useful later)
    raw: dict[str, Any] | None = None

    @property
    def unique_id(self) -> str:
        return f"iotopen:{int(self.installation_id)}:{int(self.function_id)}"

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> FunctionX:
        fid = _as_int(_get_any(d, "function_id", "functionId", "id"), 0)
        iid = _as_int(_get_any(d, "installation_id", "installationId"), 0)

        topic_read = _as_str(_get_any(d, "topic_read", "topicRead"), "")
        topic_set_v = _get_any(d, "topic_set", "topicSet")
        topic_set = _as_str(topic_set_v, "") if topic_set_v is not None else None
        if topic_set is not None and not topic_set.strip():
            topic_set = None

        friendly = _get_any(d, "friendly_name", "friendlyName", "name", default=None)
        friendly_name = _as_str(friendly, "") if friendly is not None else None
        if friendly_name is not None and not friendly_name.strip():
            friendly_name = None

        device_id_v = _get_any(d, "device_id", "deviceId", default=None)
        device_id = _as_int(device_id_v, 0) if device_id_v is not None else None
        if device_id == 0:
            device_id = None

        # state_on/off aliases
        state_on = _get_any(d, "state_on", "stateOn", "payload_on", "payloadOn", default=None)
        state_off = _get_any(d, "state_off", "stateOff", "payload_off", "payloadOff", default=None)

        return cls(
            function_id=fid,
            installation_id=iid,
            type=_as_str(_get_any(d, "type"), ""),
            topic_read=topic_read,
            topic_set=topic_set,
            friendly_name=friendly_name,
            device_id=device_id,
            state_on=state_on,
            state_off=state_off,
            raw=dict(d),
        )
