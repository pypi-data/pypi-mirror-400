# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/observability/metrics.py
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TypedDict


def _escape_label_value(v: str) -> str:
    """
    Prometheus label value escaping (text exposition format):
    escape backslash, double-quote, and newlines.
    """
    return v.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r").replace('"', '\\"')


def _norm_metric_name(name: str) -> str:
    """
    Convert a short metric name like 'supervisor_start_total' into a Prometheus-safe name.
    We also prefix with 'iotopen_bridge_' to avoid collisions.
    """
    s = str(name or "").strip()
    if not s:
        s = "unknown_total"
    s = s.replace("-", "_").replace(".", "_").replace(" ", "_")
    return f"iotopen_bridge_{s}"


class MetricsSnapshot(TypedDict):
    mqtt_rx_total: int
    per_topic: dict[str, int]
    counters: dict[str, int]
    gauges: dict[str, float]


@dataclass
class Metrics:
    """
    Minimal metrics surface.

    Provides:
      - on_mqtt_message(topic=...)
      - render_prometheus()
      - inc(name, amount=1)
      - set_gauge(name, value)

    When disabled, hooks become no-ops and rendered output stays valid but static.
    """

    enabled: bool = True

    _lock: threading.RLock = field(default_factory=threading.RLock, init=False)
    _mqtt_rx_total: int = field(default=0, init=False)
    _per_topic: dict[str, int] = field(default_factory=dict, init=False)

    # Generic counters/gauges used by runtime/supervisor.
    _counters: dict[str, int] = field(default_factory=dict, init=False)
    _gauges: dict[str, float] = field(default_factory=dict, init=False)

    def on_mqtt_message(self, *, topic: str) -> None:
        if not bool(self.enabled):
            return
        t = str(topic or "")
        with self._lock:
            self._mqtt_rx_total += 1
            self._per_topic[t] = int(self._per_topic.get(t, 0)) + 1

    # Backwards/alt hook name (runtime tries both)
    def mqtt_on_message(self, topic: str) -> None:
        self.on_mqtt_message(topic=str(topic))

    def inc(self, name: str, amount: int = 1) -> None:
        """Increment a named counter (used by supervisor)."""
        if not bool(self.enabled):
            return
        key = str(name or "")
        step = int(amount or 1)
        with self._lock:
            self._counters[key] = int(self._counters.get(key, 0)) + step

    def set_gauge(self, name: str, value: float) -> None:
        """Set a named gauge (used by supervisor)."""
        if not bool(self.enabled):
            return
        key = str(name or "")
        val = float(value)
        with self._lock:
            self._gauges[key] = val

    def snapshot(self) -> MetricsSnapshot:
        """Useful for debugging / unit tests."""
        with self._lock:
            return {
                "mqtt_rx_total": int(self._mqtt_rx_total),
                "per_topic": dict(self._per_topic),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
            }

    def render_prometheus(self) -> str:
        """
        Render Prometheus text format.
        The unlabeled counter must always appear (even at 0).
        """
        snap = self.snapshot()
        rx = snap["mqtt_rx_total"]
        per = snap["per_topic"]
        counters = snap["counters"]
        gauges = snap["gauges"]

        lines: list[str] = []

        # Built-in MQTT counters
        lines.append(
            "# HELP iotopen_bridge_mqtt_rx_messages_total Total MQTT messages received by the bridge."
        )
        lines.append("# TYPE iotopen_bridge_mqtt_rx_messages_total counter")
        lines.append(f"iotopen_bridge_mqtt_rx_messages_total {int(rx)}")

        lines.append(
            "# HELP iotopen_bridge_mqtt_messages_total Total MQTT messages received by topic."
        )
        lines.append("# TYPE iotopen_bridge_mqtt_messages_total counter")
        for topic, count in sorted(per.items()):
            tv = _escape_label_value(str(topic))
            lines.append(f'iotopen_bridge_mqtt_messages_total{{topic="{tv}"}} {int(count)}')

        # Generic counters
        for name, count in sorted(counters.items()):
            metric = _norm_metric_name(name)
            lines.append(f"# TYPE {metric} counter")
            lines.append(f"{metric} {int(count)}")

        # Generic gauges
        for name, val in sorted(gauges.items()):
            metric = _norm_metric_name(name)
            lines.append(f"# TYPE {metric} gauge")
            lines.append(f"{metric} {float(val)}")

        return "\n".join(lines) + "\n"
