# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/crypto/nonce.py
from __future__ import annotations

import base64
import os
import re

_NONCE_RE = re.compile(r"^[A-Za-z0-9_-]{8,128}$")


def new_nonce_b64u(nbytes: int = 16) -> str:
    """Generate a random base64url (no padding) nonce."""
    raw = os.urandom(int(nbytes))
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def is_valid_nonce(nonce: str) -> bool:
    """Basic format validation for nonces (base64url-ish, bounded length)."""
    return bool(_NONCE_RE.fullmatch(str(nonce or "")))
