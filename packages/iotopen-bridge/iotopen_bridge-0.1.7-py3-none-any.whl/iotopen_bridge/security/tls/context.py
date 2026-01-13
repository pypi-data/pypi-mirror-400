# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/tls/context.py
from __future__ import annotations

import contextlib
import ssl
from typing import Any

from .profiles import TLSSettings, profile_ciphers, profile_min_version
from .verify import set_verify_mode


def build_ssl_context(tls: TLSSettings | dict[str, Any] | object) -> ssl.SSLContext:
    """Build an SSLContext for MQTT client TLS."""
    settings = TLSSettings.from_any(tls)

    # create_default_context() already loads system default CA certificates
    # when no cafile/capath/cadata is provided. (Avoid redundant loads.)
    ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

    # If user provided a CA file, add it (common for private PKI / Mosquitto setups).
    if getattr(settings, "cafile", None):
        with contextlib.suppress(Exception):
            ctx.load_verify_locations(cafile=settings.cafile)

    set_verify_mode(
        ctx,
        insecure=bool(getattr(settings, "insecure", False)),
        verify_hostname=bool(getattr(settings, "verify_hostname", True)),
    )

    with contextlib.suppress(Exception):
        ctx.minimum_version = profile_min_version(getattr(settings, "profile", "") or "")

    cipher_str = profile_ciphers(getattr(settings, "profile", "") or "")
    if cipher_str:
        with contextlib.suppress(Exception):
            ctx.set_ciphers(cipher_str)

    client_cert = getattr(settings, "client_cert", None)
    if client_cert:
        ctx.load_cert_chain(
            certfile=client_cert,
            keyfile=getattr(settings, "client_key", None) or None,
        )

    return ctx
