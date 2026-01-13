# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os
from dataclasses import dataclass
from types import ModuleType
from typing import Any

_trace: ModuleType | None
try:
    from opentelemetry import trace as _trace  # opentelemetry-api
except ModuleNotFoundError:  # pragma: no cover
    _trace = None


def _env_bool(name: str, default: bool = False) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    if not v:
        return default
    return v in {"1", "true", "t", "yes", "y", "on"}


@dataclass(frozen=True, slots=True)
class TracingConfig:
    enabled: bool = False
    console_exporter: bool = False
    service_name: str = "iotopen-bridge"


def load_tracing_config(service_name: str = "iotopen-bridge") -> TracingConfig:
    return TracingConfig(
        enabled=_env_bool("IOTOPEN_BRIDGE_TRACING_ENABLED", False),
        console_exporter=_env_bool("IOTOPEN_BRIDGE_TRACING_CONSOLE", False),
        service_name=service_name,
    )


def configure_tracing(service_name: str = "iotopen-bridge") -> Any | None:
    """Configure tracing if enabled and opentelemetry-sdk is available; otherwise no-op."""
    cfg = load_tracing_config(service_name=service_name)
    if not cfg.enabled or _trace is None:
        return None

    try:
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    except ModuleNotFoundError:
        # opentelemetry-sdk not installed -> tracing disabled
        return None

    resource = Resource.create({"service.name": cfg.service_name})
    provider = TracerProvider(resource=resource)

    if cfg.console_exporter:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    _trace.set_tracer_provider(provider)
    return provider


def get_tracer(name: str = "iotopen-bridge") -> Any:
    """Return a tracer if opentelemetry-api is installed; otherwise a tiny no-op tracer."""
    if _trace is None:

        class _NoopTracer:
            def start_as_current_span(self, *_: Any, **__: Any) -> Any:
                from contextlib import nullcontext

                return nullcontext()

        return _NoopTracer()

    return _trace.get_tracer(name)
