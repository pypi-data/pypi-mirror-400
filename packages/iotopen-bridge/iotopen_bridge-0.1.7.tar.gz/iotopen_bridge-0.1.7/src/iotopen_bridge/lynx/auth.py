# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/lynx/auth.py
"""Authentication helper for IoT Open Lynx REST API.

IoT Open documentation and examples show multiple authentication schemes:

- API key in an ``X-API-Key`` header
- HTTP Basic where the username is ``token`` and the password is the API key

To minimize integration friction, the default mode is ``auto`` which sends BOTH
headers. Servers typically accept one of them and ignore the other.

You can force a single mode via configuration if needed.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass


@dataclass(frozen=True)
class LynxAuth:
    """Auth settings for REST calls."""

    api_key: str
    # Supported:
    #   - "auto" (default): send both X-API-Key and Basic token:<api_key>
    #   - "x-api-key": send only X-API-Key
    #   - "basic": send only Authorization: Basic ...
    #   - "bearer": legacy/compat
    mode: str = "auto"
    # Used only for basic auth. IoT Open examples commonly use username 'token'.
    username: str = "token"

    def headers(self) -> dict[str, str]:
        key = str(self.api_key or "").strip()
        mode = str(self.mode or "auto").strip().lower().replace("_", "-")

        def _basic_header(user: str, password: str) -> str:
            token = base64.b64encode(f"{user}:{password}".encode()).decode("ascii")
            return f"Basic {token}"

        if mode in {"auto", "default"}:
            # Send both; backend will typically accept one.
            return {
                "X-API-Key": key,
                "Authorization": _basic_header(str(self.username or "token"), key),
            }

        if mode in {"x-api-key", "apikey", "api-key", "xapikey"}:
            return {"X-API-Key": key}

        if mode in {"basic", "basic-auth", "basicauth"}:
            user = str(self.username or "token")
            return {"Authorization": _basic_header(user, key)}

        if mode in {"bearer", "oauth", "oauth2"}:
            return {"Authorization": f"Bearer {key}"}

        # Fallback.
        return {"X-API-Key": key}
