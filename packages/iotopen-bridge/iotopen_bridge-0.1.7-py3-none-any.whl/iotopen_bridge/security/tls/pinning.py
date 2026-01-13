# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/tls/pinning.py
from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass


def sha256_fingerprint(der_bytes: bytes) -> str:
    return hashlib.sha256(der_bytes).hexdigest()


@dataclass(frozen=True)
class Pinset:
    """Optional certificate pinning helper (not wired by default).

    If you later want to pin the broker cert, you can compare the peer DER cert.
    """

    sha256_hex: tuple[str, ...] = ()

    @classmethod
    def from_iterable(cls, pins: Iterable[str] | None) -> Pinset:
        if not pins:
            return Pinset(())
        norm = []
        for p in pins:
            s = str(p or "").strip().lower()
            if not s:
                continue
            # allow "AA:BB:.." or plain hex
            s = s.replace(":", "")
            if len(s) == 64:
                norm.append(s)
        return Pinset(tuple(sorted(set(norm))))

    def matches(self, der_cert: bytes) -> bool:
        if not self.sha256_hex:
            return True
        fp = sha256_fingerprint(der_cert)
        return fp in set(self.sha256_hex)
