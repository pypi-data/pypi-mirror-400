# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/tls/profiles.py
from __future__ import annotations

import ssl
from dataclasses import dataclass
from typing import Any


def _to_bool(v: Any, default: bool = False) -> bool:
    if isinstance(v, bool):
        return v
    s = str(v or "").strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off", ""):
        return False
    return default


def _to_str(v: Any, default: str = "") -> str:
    s = str(v or "").strip()
    return s if s else default


@dataclass(frozen=True)
class TLSSettings:
    """Normalized TLS settings used by transport.

    NOTE: Keep independent from BridgeConfig.TLSConfig so transport can be reused.
    """

    enabled: bool = False
    cafile: str | None = None
    verify_hostname: bool = True
    insecure: bool = False
    profile: str = "modern"  # modern | intermediate | legacy
    client_cert: str | None = None
    client_key: str | None = None

    @classmethod
    def from_any(cls, obj: Any) -> TLSSettings:
        if isinstance(obj, TLSSettings):
            return obj

        if obj is None:
            return TLSSettings()

        to_settings = getattr(obj, "to_settings", None)
        if callable(to_settings):
            try:
                return cls.from_any(to_settings())
            except Exception:
                pass

        if isinstance(obj, dict):
            d: dict[str, Any] = dict(obj)
            return TLSSettings(
                enabled=_to_bool(d.get("enabled"), False),
                cafile=d.get("cafile") or None,
                verify_hostname=_to_bool(d.get("verify_hostname"), True),
                insecure=_to_bool(d.get("insecure"), False),
                profile=_to_str(d.get("profile"), "modern"),
                client_cert=d.get("client_cert") or None,
                client_key=d.get("client_key") or None,
            )

        return TLSSettings(
            enabled=_to_bool(getattr(obj, "enabled", False), False),
            cafile=getattr(obj, "cafile", None),
            verify_hostname=_to_bool(getattr(obj, "verify_hostname", True), True),
            insecure=_to_bool(getattr(obj, "insecure", False), False),
            profile=_to_str(getattr(obj, "profile", "modern"), "modern"),
            client_cert=getattr(obj, "client_cert", None),
            client_key=getattr(obj, "client_key", None),
        )


def profile_min_version(profile: str) -> ssl.TLSVersion:
    p = str(profile or "").strip().lower()
    if p in ("modern", "intermediate", ""):
        return ssl.TLSVersion.TLSv1_2
    return ssl.TLSVersion.TLSv1


def profile_ciphers(profile: str) -> str | None:
    """Return cipher string or None to keep OpenSSL defaults."""
    p = str(profile or "").strip().lower()
    if p in ("modern", ""):
        return "ECDHE+AESGCM:ECDHE+CHACHA20:ECDHE+AES"
    if p == "intermediate":
        return "ECDHE+AESGCM:ECDHE+AES"
    if p == "legacy":
        return "HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4"
    return None
