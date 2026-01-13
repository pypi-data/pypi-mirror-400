# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/cli/commands/probe_mqtt.py
from __future__ import annotations

import contextlib
import time
from typing import Any

from ...adapters.raw_capture import RawCapture
from ...bridge.config import BridgeConfig
from ...security.tls.profiles import TLSSettings
from ...transport.mqtt.paho_client import PahoMqttClient, PahoMqttConfig


def cmd_probe_mqtt(args: Any) -> int:
    """Connect to MQTT, optionally subscribe, optionally publish, and print received messages."""
    cfg = BridgeConfig.from_file(args.config)

    client_id_base = (cfg.mqtt.client_id or "iotopen-bridge").strip()
    client_id = f"{client_id_base}-probe"

    mqtt_cfg = PahoMqttConfig(
        host=cfg.mqtt.host,
        port=int(cfg.mqtt.port),
        username=cfg.mqtt.username,
        password=cfg.mqtt.password,
        client_id=client_id,
        keepalive=int(cfg.mqtt.keepalive),
        tls=TLSSettings.from_any(cfg.mqtt.tls),
    )

    raw_capture = RawCapture(cfg.raw_capture)

    client = PahoMqttClient(cfg=mqtt_cfg, raw_capture=raw_capture)

    counter: dict[str, int] = {"n": 0}

    def on_connect(ok: bool, reason: str) -> None:
        print("connected" if ok else "disconnected", reason)

        if not ok:
            return

        for topic in getattr(args, "sub", []) or []:
            client.subscribe(str(topic), qos=0)

        pub_topic = getattr(args, "pub_topic", None)
        pub_payload = getattr(args, "pub_payload", None)
        if pub_topic and pub_payload is not None:
            client.publish(str(pub_topic), str(pub_payload), qos=1, retain=False)

    def on_message(topic: str, payload: bytes, qos: int, retain: bool) -> None:
        counter["n"] += 1
        print(
            {
                "topic": topic,
                "payload": payload.decode("utf-8", errors="replace"),
                "qos": int(qos),
                "retain": bool(retain),
            }
        )

        target = getattr(args, "count", None)
        if target and counter["n"] >= int(target):
            client.disconnect()

    client.set_on_connect(on_connect)
    client.set_on_message(on_message)
    client.connect()

    try:
        while True:
            time.sleep(0.2)
            target = getattr(args, "count", None)
            if target and counter["n"] >= int(target):
                break
    except KeyboardInterrupt:
        with contextlib.suppress(Exception):
            client.disconnect()

    return 0
