# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/crypto/hmac_sign.py
from __future__ import annotations

import base64
import hashlib
import hmac

BytesOrStr = bytes | str


def _to_bytes(value: BytesOrStr, *, encoding: str = "utf-8") -> bytes:
    if isinstance(value, bytes):
        return value
    return str(value).encode(encoding)


def _b64u_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def hmac_sha256(key: bytes, message: BytesOrStr) -> bytes:
    """Raw HMAC-SHA256 digest."""
    return hmac.new(key, _to_bytes(message), hashlib.sha256).digest()


def hmac_sha256_b64u(key: bytes, message: BytesOrStr) -> str:
    """HMAC-SHA256, base64url (no padding)."""
    return _b64u_encode(hmac_sha256(key, message))


def verify_hmac_sha256_b64u(key: bytes, message: BytesOrStr, sig_b64u: str) -> bool:
    """Constant-time verify of a base64url signature."""
    expected = hmac_sha256_b64u(key, message)
    return hmac.compare_digest(str(sig_b64u or ""), expected)
