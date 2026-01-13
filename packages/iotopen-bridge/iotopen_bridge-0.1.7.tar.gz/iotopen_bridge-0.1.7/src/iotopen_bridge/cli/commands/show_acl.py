# File: src/iotopen_bridge/cli/commands/show_acl.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any

from ...bridge.config import BridgeConfig
from ...security.authz.acl_hinting import render_mosquitto_acl
from ...storage.sqlite_store import SQLiteStore


def cmd_show_acl(args: Any) -> int:
    """Print a Mosquitto ACL hint derived from stored inventory."""
    cfg = BridgeConfig.from_file(args.config)

    store = SQLiteStore(cfg.storage_path)
    inv = store.load_inventory(cfg.lynx.installation_id)

    allow: set[str] = set()
    if inv:
        for f in inv.functions:
            topic_read = f.get("topic_read")
            if topic_read:
                allow.add(str(topic_read))
            topic_set = f.get("topic_set")
            if topic_set:
                allow.add(str(topic_set))

    hint = render_mosquitto_acl(
        cfg.mqtt.username or "iotopen_bridge",
        sorted(allow),
        cfg.ha.discovery.prefix,
        cfg.ha.state_prefix,
    )
    print("\n".join(hint.lines))
    return 0
