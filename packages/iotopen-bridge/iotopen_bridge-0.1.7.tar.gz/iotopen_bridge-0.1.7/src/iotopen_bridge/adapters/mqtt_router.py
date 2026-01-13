# File: src/iotopen_bridge/adapters/mqtt_router.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass

from ..controllers.commands import CommandsController
from ..controllers.telemetry import TelemetryController


@dataclass
class MqttRouter:
    """Route incoming MQTT messages into the correct controller.

    Rules (default, backwards-compatible):
      1) <state_prefix>/<iid>/<fid>/set                -> CommandsController.handle_ha_set (legacy switch)
      2) <state_prefix>/<iid>/<fid>/<kind>/set         -> CommandsController.handle_ha_set(..., subkey=<kind>) (extended)
      3) everything else                               -> TelemetryController.handle_message

    With dual-MQTT:
      - source="downstream": ONLY accept /set commands; ignore other topics (avoid feeding HA topics into telemetry)
      - source="upstream": treat everything as telemetry (topic_read streams)
    """

    telemetry: TelemetryController
    commands: CommandsController
    state_prefix: str

    def on_message(
        self,
        topic: str,
        payload: bytes,
        qos: int,
        retain: bool,
        *,
        source: str | None = None,
    ) -> None:
        # Downstream broker should only drive HA commands (/set). Do not treat other downstream topics as telemetry.
        if source == "downstream":
            parsed_legacy = self._parse_ha_set_topic(topic)
            if parsed_legacy is not None:
                installation_id, function_id = parsed_legacy
                self.commands.handle_ha_set(installation_id, function_id, payload)
            else:
                parsed_kind = self._parse_ha_set_kind_topic(topic)
                if parsed_kind is not None:
                    installation_id, function_id, kind = parsed_kind
                    self.commands.handle_ha_set(installation_id, function_id, payload, subkey=kind)
            return

        # Upstream/default behavior:
        parsed_legacy = self._parse_ha_set_topic(topic)
        if parsed_legacy is not None:
            installation_id, function_id = parsed_legacy
            self.commands.handle_ha_set(installation_id, function_id, payload)
            return

        parsed_kind = self._parse_ha_set_kind_topic(topic)
        if parsed_kind is not None:
            installation_id, function_id, kind = parsed_kind
            self.commands.handle_ha_set(installation_id, function_id, payload, subkey=kind)
            return

        self.telemetry.handle_message(topic, payload, qos, retain)

    def _parse_ha_set_topic(self, topic: str) -> tuple[int, int] | None:
        # Expected: <state_prefix>/<iid>/<fid>/set
        parts = [p for p in str(topic).split("/") if p]
        prefix_parts = [p for p in str(self.state_prefix).split("/") if p]

        need_len = len(prefix_parts) + 3
        if len(parts) != need_len:
            return None
        if parts[: len(prefix_parts)] != prefix_parts:
            return None
        if parts[-1] != "set":
            return None

        inst_s = parts[len(prefix_parts)]
        fid_s = parts[len(prefix_parts) + 1]
        try:
            return int(inst_s), int(fid_s)
        except Exception:
            return None

    def _parse_ha_set_kind_topic(self, topic: str) -> tuple[int, int, str] | None:
        # Expected: <state_prefix>/<iid>/<fid>/<kind>/set
        parts = [p for p in str(topic).split("/") if p]
        prefix_parts = [p for p in str(self.state_prefix).split("/") if p]

        need_len = len(prefix_parts) + 4
        if len(parts) != need_len:
            return None
        if parts[: len(prefix_parts)] != prefix_parts:
            return None
        if parts[-1] != "set":
            return None

        inst_s = parts[len(prefix_parts)]
        fid_s = parts[len(prefix_parts) + 1]
        kind = parts[len(prefix_parts) + 2]
        try:
            return int(inst_s), int(fid_s), str(kind)
        except Exception:
            return None
