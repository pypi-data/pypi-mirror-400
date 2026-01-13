# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/lynx/endpoint.py

from __future__ import annotations


def normalize_base_url(base_url: str) -> str:
    """
    Ensure base_url has a scheme and no trailing slash.
    Accepts:
      - https://lynx.iotopen.se
      - lynx.iotopen.se   -> https://lynx.iotopen.se
    """
    url = (base_url or "").strip()
    if not url:
        return "https://lynx.iotopen.se"

    if "://" not in url:
        url = "https://" + url

    return url.rstrip("/")


def _join(base_url: str, path: str) -> str:
    base = normalize_base_url(base_url)
    if not path.startswith("/"):
        path = "/" + path
    return base + path


# ---- API v2 (per Lynx API docs) ----
def functionx_url(base_url: str, installation_id: int) -> str:
    return _join(base_url, f"/api/v2/functionx/{int(installation_id)}")


def status_url(base_url: str, installation_id: int) -> str:
    return _join(base_url, f"/api/v2/status/{int(installation_id)}")
