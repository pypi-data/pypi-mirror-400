# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/crypto/envelope.py
from __future__ import annotations

import base64
import json
import os
import re
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .hmac_sign import hmac_sha256_b64u, verify_hmac_sha256_b64u
from .nonce import is_valid_nonce, new_nonce_b64u


def _b64u_decode(s: str) -> bytes:
    padded = s + "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _parse_key(value: str) -> bytes:
    """Parse a signing key from env/config.

    Accepted forms:
      - base64url/base64 (recommended)
      - hex (prefix `hex:` or all-hex)
      - raw string (prefix `raw:`)
    """
    v = (value or "").strip()
    if not v:
        return b""

    if v.startswith("raw:"):
        return v[4:].encode("utf-8")

    if v.startswith("hex:"):
        return bytes.fromhex(v[4:])

    hv = v.lower()
    if re.fullmatch(r"[0-9a-f]+", hv or "") and len(hv) % 2 == 0:
        try:
            return bytes.fromhex(hv)
        except Exception:
            pass

    try:
        return _b64u_decode(v)
    except Exception:
        return v.encode("utf-8")


def _canonical_json(obj: Any) -> str:
    return json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def _now_s() -> int:
    return int(time.time())


NonceSeenFn = Callable[[str, str, int, int], bool]
"""Return True if (kid, nonce) is already seen; otherwise False."""


@dataclass(frozen=True, slots=True)
class EnvelopeSettings:
    """Runtime settings for signed MQTT command envelopes.

    Behavior is *disabled* unless `key` is present.
    """

    enabled: bool = False
    kid: str = "default"
    key: bytes = b""
    alg: str = "HS256"

    max_skew_seconds: int = 300
    nonce_ttl_seconds: int = 3600

    @classmethod
    def from_env(cls) -> EnvelopeSettings:
        key_s = (os.environ.get("IOTOPEN_BRIDGE_COMMAND_SIGNING_KEY") or "").strip()
        kid = (
            os.environ.get("IOTOPEN_BRIDGE_COMMAND_SIGNING_KID") or "default"
        ).strip() or "default"
        max_skew = int(os.environ.get("IOTOPEN_BRIDGE_COMMAND_SIGNING_MAX_SKEW", "300") or "300")
        ttl = int(os.environ.get("IOTOPEN_BRIDGE_COMMAND_SIGNING_NONCE_TTL", "3600") or "3600")
        key_b = _parse_key(key_s) if key_s else b""
        return cls(
            enabled=bool(key_b),
            kid=kid,
            key=key_b,
            max_skew_seconds=max_skew,
            nonce_ttl_seconds=ttl,
        )


@dataclass(frozen=True, slots=True)
class CommandEnvelope:
    v: Any
    ts: int
    nonce: str
    alg: str = "HS256"
    kid: str = "default"
    sig: str = ""

    def signing_payload(self) -> Mapping[str, Any]:
        return {
            "alg": self.alg,
            "kid": self.kid,
            "nonce": self.nonce,
            "ts": int(self.ts),
            "v": self.v,
        }

    def signing_input(self) -> str:
        return _canonical_json(self.signing_payload())

    def to_dict(self) -> dict[str, Any]:
        d = dict(self.signing_payload())
        d["sig"] = self.sig
        return d

    def to_json(self) -> str:
        return _canonical_json(self.to_dict())


def wrap_command(
    value: Any,
    *,
    settings: EnvelopeSettings,
    ts: int | None = None,
    nonce: str | None = None,
) -> CommandEnvelope:
    if not settings.enabled:
        raise ValueError("Envelope signing is disabled (no key configured)")
    if settings.alg != "HS256":
        raise ValueError(f"Unsupported alg: {settings.alg}")

    ts_i = int(ts if ts is not None else _now_s())
    nn = str(nonce or new_nonce_b64u())
    if not is_valid_nonce(nn):
        raise ValueError("Invalid nonce format")

    env = CommandEnvelope(v=value, ts=ts_i, nonce=nn, alg=settings.alg, kid=settings.kid, sig="")
    sig = hmac_sha256_b64u(settings.key, env.signing_input())
    return CommandEnvelope(v=value, ts=ts_i, nonce=nn, alg=settings.alg, kid=settings.kid, sig=sig)


def _maybe_parse_json(payload: bytes | str) -> Any:
    s = payload.decode("utf-8", errors="strict") if isinstance(payload, bytes) else str(payload)
    s = s.strip()
    if not s:
        return None
    return json.loads(s)


@dataclass(frozen=True, slots=True)
class UnwrapResult:
    ok: bool
    value: Any = None
    envelope: CommandEnvelope | None = None
    error: str | None = None


def unwrap_command(
    payload: bytes | str,
    *,
    settings: EnvelopeSettings,
    nonce_seen: NonceSeenFn | None = None,
    now_s: int | None = None,
) -> UnwrapResult:
    """Verify and unwrap an envelope, falling back to legacy payloads.

    - If settings.enabled is False: passthrough.
    - If payload isn't a matching envelope object: passthrough (JSON or raw string).
    """
    if not settings.enabled:
        if isinstance(payload, bytes):
            return UnwrapResult(ok=True, value=payload.decode("utf-8", errors="replace"))
        return UnwrapResult(ok=True, value=payload)

    try:
        obj = _maybe_parse_json(payload)
    except Exception:
        if isinstance(payload, bytes):
            return UnwrapResult(ok=True, value=payload.decode("utf-8", errors="replace"))
        return UnwrapResult(ok=True, value=payload)

    if not isinstance(obj, dict):
        return UnwrapResult(ok=True, value=obj)

    if not {"v", "ts", "nonce", "sig"}.issubset(obj.keys()):
        return UnwrapResult(ok=True, value=obj)

    try:
        env = CommandEnvelope(
            v=obj.get("v"),
            ts=int(obj.get("ts") or 0),
            nonce=str(obj.get("nonce") or ""),
            alg=str(obj.get("alg") or "HS256"),
            kid=str(obj.get("kid") or settings.kid or "default"),
            sig=str(obj.get("sig") or ""),
        )
    except Exception as e:
        return UnwrapResult(ok=False, error=f"invalid envelope fields: {e}")

    if env.alg != "HS256":
        return UnwrapResult(ok=False, envelope=env, error=f"unsupported alg: {env.alg}")

    if not env.nonce or not is_valid_nonce(env.nonce):
        return UnwrapResult(ok=False, envelope=env, error="invalid nonce")

    now = int(now_s if now_s is not None else _now_s())
    if env.ts <= 0:
        return UnwrapResult(ok=False, envelope=env, error="missing/invalid ts")
    if abs(now - int(env.ts)) > int(settings.max_skew_seconds):
        return UnwrapResult(ok=False, envelope=env, error="ts outside allowed skew")

    if nonce_seen is not None:
        try:
            replay = bool(
                nonce_seen(env.kid, env.nonce, int(env.ts), int(settings.nonce_ttl_seconds))
            )
        except Exception:
            return UnwrapResult(ok=False, envelope=env, error="nonce store error")
        if replay:
            return UnwrapResult(ok=False, envelope=env, error="replay detected")

    if not verify_hmac_sha256_b64u(settings.key, env.signing_input(), env.sig):
        return UnwrapResult(ok=False, envelope=env, error="bad signature")

    return UnwrapResult(ok=True, value=env.v, envelope=env)
