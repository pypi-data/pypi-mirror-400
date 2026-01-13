# File: src/iotopen_bridge/converters/ha_discovery/topics.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations


def discovery_config_topic(prefix: str, component: str, object_id: str) -> str:
    """Return Home Assistant MQTT discovery config topic.

    Format: <discovery_prefix>/<component>/<object_id>/config
    """
    dp = str(prefix or "").strip("/")
    comp = str(component or "").strip("/")
    obj = str(object_id or "").strip("/")
    return f"{dp}/{comp}/{obj}/config"
