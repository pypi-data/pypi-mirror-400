# File: src/iotopen_bridge/models/mqtt.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Qos(int, Enum):
    """MQTT QoS levels."""

    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2


@dataclass(frozen=True, slots=True)
class TopicSpec:
    """Topic intent used by routing/adapters (tiny, dependency-free)."""

    topic: str
    qos: Qos = Qos.AT_MOST_ONCE
    retain: bool = False
    purpose: str = "telemetry"
