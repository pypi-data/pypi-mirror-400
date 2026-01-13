# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/tls/profiles.py
from __future__ import annotations

import ssl
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


def _to_bool(v: Any, default: bool = False) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return default
    s = str(v).strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off", ""):
        return False
    return default


def _to_str(v: Any, default: str = "") -> str:
    s = str(v or "").strip()
    return s if s else default


def _to_opt_str(v: Any) -> str | None:
    s = str(v or "").strip()
    return s or None


def _norm_profile(p: Any, default: str = "modern") -> str:
    s = str(p or "").strip().lower()
    if s in ("", "modern"):
        return "modern"
    if s in ("intermediate", "compat"):
        return "intermediate"
    if s in ("legacy", "old"):
        return "legacy"
    return default


def _normalize(settings: TLSSettings) -> TLSSettings:
    # If you explicitly set insecure, we treat it as "skip verification posture".
    # That implies hostname verification cannot be meaningful.
    if settings.insecure and settings.verify_hostname:
        return TLSSettings(
            enabled=settings.enabled,
            cafile=settings.cafile,
            verify_hostname=False,
            insecure=True,
            profile=_norm_profile(settings.profile, "modern"),
            client_cert=settings.client_cert,
            client_key=settings.client_key,
        )

    # Normalize profile string even when already set.
    prof = _norm_profile(settings.profile, "modern")
    if prof != settings.profile:
        return TLSSettings(
            enabled=settings.enabled,
            cafile=settings.cafile,
            verify_hostname=settings.verify_hostname,
            insecure=settings.insecure,
            profile=prof,
            client_cert=settings.client_cert,
            client_key=settings.client_key,
        )

    return settings


@dataclass(frozen=True, slots=True)
class TLSSettings:
    """Normalized TLS settings used by transport.

    Fields:
      enabled:
        Whether TLS should be used at all.
      cafile:
        CA bundle to trust (recommended).
      verify_hostname:
        Whether to verify broker hostname (SNI/hostname check).
      insecure:
        Insecure posture. Intended meaning: skip verification (chain/hostname).
        (Your build_ssl_context() should map this to CERT_NONE + check_hostname=False.)
      profile:
        modern | intermediate | legacy (influences min TLS version + optional ciphers)
      client_cert/client_key:
        Optional client authentication (mTLS).
    """

    enabled: bool = False
    cafile: str | None = None

    # Hostname verification posture
    verify_hostname: bool = True

    # Insecure posture (explicit). When True, verify_hostname will be forced False.
    insecure: bool = False

    # modern | intermediate | legacy
    profile: str = "modern"

    # mTLS
    client_cert: str | None = None
    client_key: str | None = None

    @property
    def has_client_auth(self) -> bool:
        return bool(self.client_cert) or bool(self.client_key)

    @classmethod
    def from_any(cls, obj: Any) -> TLSSettings:
        """Coerce TLS settings from:
        - TLSSettings
        - Mapping/dict-like
        - BridgeConfig.TLSConfig (has to_settings())
        """
        if isinstance(obj, TLSSettings):
            return _normalize(obj)

        if obj is None:
            return TLSSettings()

        # BridgeConfig.TLSConfig has .to_settings()
        to_settings = getattr(obj, "to_settings", None)
        if callable(to_settings):
            try:
                return cls.from_any(to_settings())
            except Exception:
                pass

        # Mapping/dict-like (support common aliases)
        if isinstance(obj, Mapping):
            d = dict(obj)

            # Aliases (keep your existing keys, just accept more)
            cafile = _to_opt_str(
                d.get("cafile") or d.get("ca_file") or d.get("ca_cert") or d.get("ca_bundle")
            )
            client_cert = _to_opt_str(
                d.get("client_cert") or d.get("certfile") or d.get("cert_file")
            )
            client_key = _to_opt_str(d.get("client_key") or d.get("keyfile") or d.get("key_file"))

            verify_hostname = _to_bool(
                d.get("verify_hostname", d.get("check_hostname", True)),
                True,
            )

            # Allow "verify" / "verify_cert" inversions if provided
            verify_cert = d.get("verify_cert", d.get("verify"))
            insecure = _to_bool(d.get("insecure"), False)
            if verify_cert is not None:
                insecure = not _to_bool(verify_cert, True)

            # If user omitted "enabled" but provided TLS-relevant fields, infer enabled=True.
            if "enabled" in d:
                enabled = _to_bool(d.get("enabled"), False)
            else:
                enabled = any(
                    x is not None
                    for x in (
                        cafile,
                        client_cert,
                        client_key,
                        d.get("profile"),
                        d.get("insecure"),
                        d.get("verify_hostname"),
                        d.get("check_hostname"),
                        d.get("verify"),
                        d.get("verify_cert"),
                    )
                )

            settings = TLSSettings(
                enabled=enabled,
                cafile=cafile,
                verify_hostname=verify_hostname,
                insecure=insecure,
                profile=_norm_profile(d.get("profile"), "modern"),
                client_cert=client_cert,
                client_key=client_key,
            )
            return _normalize(settings)

        # best-effort attribute read (+ alias attributes)
        cafile = _to_opt_str(getattr(obj, "cafile", None) or getattr(obj, "ca_file", None))
        client_cert = _to_opt_str(
            getattr(obj, "client_cert", None) or getattr(obj, "certfile", None)
        )
        client_key = _to_opt_str(getattr(obj, "client_key", None) or getattr(obj, "keyfile", None))

        settings = TLSSettings(
            enabled=_to_bool(getattr(obj, "enabled", False), False),
            cafile=cafile,
            verify_hostname=_to_bool(
                getattr(obj, "verify_hostname", getattr(obj, "check_hostname", True)),
                True,
            ),
            insecure=_to_bool(getattr(obj, "insecure", False), False),
            profile=_norm_profile(getattr(obj, "profile", "modern"), "modern"),
            client_cert=client_cert,
            client_key=client_key,
        )
        return _normalize(settings)


def _tlsver(name: str, fallback: ssl.TLSVersion) -> ssl.TLSVersion:
    return getattr(ssl.TLSVersion, name, fallback)


def profile_min_version(profile: str) -> ssl.TLSVersion:
    p = str(profile or "").strip().lower()
    # modern/intermediate == TLSv1.2+ baseline (broadly compatible + safe default).
    if p in ("modern", "intermediate", ""):
        return _tlsver("TLSv1_2", ssl.TLSVersion.MINIMUM_SUPPORTED)
    # legacy only if you absolutely must talk to old brokers
    return _tlsver("TLSv1", ssl.TLSVersion.MINIMUM_SUPPORTED)


def profile_ciphers(profile: str) -> str | None:
    """Optional cipher string. Return None to keep OpenSSL defaults.

    We avoid over-constraining ciphers because OpenSSL + platform builds differ.
    """
    p = str(profile or "").strip().lower()
    if p in ("modern", ""):
        # Prefer AEAD + ECDHE; keep it compatible with most brokers.
        return "ECDHE+AESGCM:ECDHE+CHACHA20:ECDHE+AES"
    if p == "intermediate":
        return "ECDHE+AESGCM:ECDHE+AES"
    if p == "legacy":
        # Allow older suites if broker is ancient. Still not enabling NULL/EXPORT.
        return "HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4"
    return None
