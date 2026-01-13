# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/converters/payload/__init__.py
from __future__ import annotations

from .adapters import (
    DefaultJsonAdapter,
    PayloadAdapter,
    ShellyGen2RpcAdapter,
    TasmotaAdapter,
    Zigbee2MQTTAdapter,
    default_adapters_registry,
)
from .base import DecodeError, DecoderContext, PayloadDecoder
from .bytes_decoder import BytesDecoder
from .json_decoder import JsonDecoder
from .scalar_decoder import ScalarDecoder
from .template_decoder import TemplateDecoder

__all__ = [
    "BytesDecoder",
    "DecodeError",
    "DecoderContext",
    "DefaultJsonAdapter",
    "JsonDecoder",
    "PayloadAdapter",
    "PayloadDecoder",
    "ScalarDecoder",
    "ShellyGen2RpcAdapter",
    "TasmotaAdapter",
    "TemplateDecoder",
    "Zigbee2MQTTAdapter",
    "default_adapters_registry",
]
