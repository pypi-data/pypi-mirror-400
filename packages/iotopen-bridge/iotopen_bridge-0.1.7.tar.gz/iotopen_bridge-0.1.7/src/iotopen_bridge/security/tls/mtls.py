# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/tls/mtls.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MTLSConfig:
    client_cert: str | None = None
    client_key: str | None = None

    def enabled(self) -> bool:
        return bool(self.client_cert)
