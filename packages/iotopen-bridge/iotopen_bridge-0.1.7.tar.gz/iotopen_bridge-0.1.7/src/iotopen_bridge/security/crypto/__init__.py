# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/crypto/__init__.py
"""Crypto helpers (small, dependency-free).

- hmac_sign: HMAC-SHA256 signing/verification
- nonce: nonce generation + validation
- envelope: deterministic signed MQTT command payloads
- envelope_store: replay protection store using SQLite
"""

from .envelope import CommandEnvelope, EnvelopeSettings, UnwrapResult, unwrap_command, wrap_command
from .envelope_store import EnvelopeNonceStore
from .hmac_sign import hmac_sha256, hmac_sha256_b64u, verify_hmac_sha256_b64u
from .nonce import is_valid_nonce, new_nonce_b64u

__all__ = [
    "CommandEnvelope",
    "EnvelopeNonceStore",
    "EnvelopeSettings",
    "UnwrapResult",
    "hmac_sha256",
    "hmac_sha256_b64u",
    "is_valid_nonce",
    "new_nonce_b64u",
    "unwrap_command",
    "verify_hmac_sha256_b64u",
    "wrap_command",
]
