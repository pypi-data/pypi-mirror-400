# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/cli/commands/init_config.py
from __future__ import annotations

import getpass
from typing import Any

import yaml


def _prompt(label: str, default: str | None = None) -> str:
    if default is None:
        v = input(f"{label}: ").strip()
        while not v:
            v = input(f"{label}: ").strip()
        return v
    v = input(f"{label} [{default}]: ").strip()
    return v or default


def _prompt_secret(label: str) -> str:
    v = getpass.getpass(f"{label}: ").strip()
    while not v:
        v = getpass.getpass(f"{label}: ").strip()
    return v


def _prompt_bool(label: str, default: bool = False) -> bool:
    d = "Y/n" if default else "y/N"
    v = input(f"{label} ({d}): ").strip().lower()
    if not v:
        return default
    return v in ("y", "yes", "true", "1", "on")


def cmd_init_config(args: Any) -> int:
    out_path = args.out

    print("IoT Open Bridge - interactive config generator")
    print("Press Enter to accept defaults where offered.\n")

    # --- Lynx / API ---
    lynx_base_url = _prompt("Lynx base_url", "https://lynx.iotopen.se")
    lynx_api_key = _prompt_secret("Lynx api_key")
    installation_id = int(_prompt("Lynx installation_id", "2222"))

    # --- MQTT ---
    mqtt_host = _prompt("MQTT host", "localhost")
    use_tls = _prompt_bool("MQTT TLS", default=False)
    mqtt_port = int(_prompt("MQTT port", "8883" if use_tls else "1883"))

    mqtt_username = _prompt("MQTT username (blank for none)", "")
    mqtt_password = ""
    if mqtt_username:
        mqtt_password = _prompt_secret("MQTT password")

    mqtt_client_id = _prompt("MQTT client_id", "iotopen-bridge")

    # --- HA ---
    ha_discovery_prefix = _prompt("HA discovery prefix", "homeassistant")
    ha_state_prefix = _prompt("HA state prefix", "iotopen")

    cfg: dict[str, Any] = {
        "lynx": {
            "base_url": lynx_base_url,
            "api_key": lynx_api_key,
            "installation_id": installation_id,
        },
        "mqtt": {
            "host": mqtt_host,
            "port": mqtt_port,
            "username": mqtt_username or None,
            "password": mqtt_password or None,
            "client_id": mqtt_client_id,
            "keepalive": 60,
            "tls": {
                "enabled": bool(use_tls),
                "insecure": False,
                "verify_hostname": True,
                "cafile": None,
                "profile": "modern",
                "client_cert": None,
                "client_key": None,
            },
        },
        "ha": {
            "discovery": {"prefix": ha_discovery_prefix},
            "state_prefix": ha_state_prefix,
            "publish_attributes": True,
            "availability": {"per_entity_enabled": True, "offline_after_seconds": 120},
        },
        "scheduler": {"inventory_refresh_seconds": 60},
        "health_http": {"enabled": True, "host": "0.0.0.0", "port": 8080},
        "authz": {"mode": "disabled"},
        "storage_path": "./state/iotopen-bridge.sqlite3",
        "log_level": "INFO",
        "raw_capture": {
            "enabled": False,
            "directory": "./state/capture",
            "max_bytes_per_file": 5_000_000,
            "prefix": "mqtt",
        },
    }

    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)

    print(f"\nWrote config: {out_path}")
    print(f"Next: iotopen-bridge run --config {out_path}")
    return 0
