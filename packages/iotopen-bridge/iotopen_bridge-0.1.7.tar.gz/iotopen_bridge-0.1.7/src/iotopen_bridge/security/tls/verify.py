# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/tls/verify.py
from __future__ import annotations

import ssl


def set_verify_mode(ctx: ssl.SSLContext, *, insecure: bool, verify_hostname: bool) -> None:
    """Apply verification settings safely.

    Important: Python requires check_hostname=False when verify_mode=CERT_NONE.
    """
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return

    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.check_hostname = bool(verify_hostname)
