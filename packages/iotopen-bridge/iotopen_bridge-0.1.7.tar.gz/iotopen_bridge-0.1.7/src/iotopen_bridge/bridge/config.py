# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/bridge/config.py
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..adapters.raw_capture import RawCaptureConfig
from ..core.errors import ConfigError

_ENV_VAR_RE = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        # ``os.path.expandvars`` expands %VAR% on Windows and $VAR/${VAR} on POSIX.
        # PowerShell users typically write ${VAR} in YAML; expand it explicitly so
        # configs are portable across platforms.
        s = os.path.expandvars(value)

        def repl(m: re.Match[str]) -> str:
            key = m.group(1)
            return os.environ.get(key, m.group(0))

        return _ENV_VAR_RE.sub(repl, s)

    if isinstance(value, list):
        return [_expand_env(v) for v in value]

    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}

    return value


def _load_any(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config file not found: {path}")

    raw = p.read_text(encoding="utf-8")
    suf = p.suffix.lower()

    if suf in {".yaml", ".yml"}:
        v = yaml.safe_load(raw)
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ConfigError(f"YAML root must be a mapping/dict: {path}")
        return dict(v)

    if suf == ".json":
        v = json.loads(raw)
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ConfigError(f"JSON root must be an object/dict: {path}")
        return dict(v)

    if suf == ".toml":
        # tomllib is stdlib in Python 3.11+. For older runtimes, use tomli.
        if sys.version_info >= (3, 11):
            import tomllib  # type: ignore[import-not-found]
        else:
            import tomli as tomllib  # type: ignore[import-not-found]

        v = tomllib.loads(raw)
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ConfigError(f"TOML root must be a table/dict: {path}")
        return dict(v)

    raise ConfigError(f"Unsupported config file type: {p.suffix}")


def _as_list_str(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    if isinstance(v, tuple):
        return [str(x) for x in v if str(x).strip()]
    if isinstance(v, str):
        s = v.strip()
        return [s] if s else []
    return []


def _norm_prefix(p: Any) -> str:
    s = str(p or "").strip()
    if not s:
        return ""
    if s.startswith("/"):
        s = s[1:]
    while s.endswith("/"):
        s = s[:-1]
    return s


def _norm_prefixes(v: list[str]) -> list[str]:
    out: list[str] = []
    for p in v:
        s = _norm_prefix(p)
        if s:
            out.append(s)
    return out


@dataclass(frozen=True)
class TLSConfig:
    enabled: bool = False
    cafile: str | None = None
    verify_hostname: bool = True
    insecure: bool = False
    profile: str = "modern"
    client_cert: str | None = None
    client_key: str | None = None

    def to_settings(self) -> dict[str, Any]:
        return {
            "enabled": bool(self.enabled),
            "cafile": self.cafile,
            "verify_hostname": bool(self.verify_hostname),
            "insecure": bool(self.insecure),
            "profile": str(self.profile or "modern"),
            "client_cert": self.client_cert,
            "client_key": self.client_key,
        }


@dataclass(frozen=True)
class LynxConfig:
    base_url: str
    api_key: str
    installation_id: int


@dataclass(frozen=True)
class MQTTConfig:
    host: str
    port: int = 1883
    username: str | None = None
    password: str | None = None
    client_id: str = "iotopen-bridge"
    keepalive: int = 60
    tls: TLSConfig = field(default_factory=TLSConfig)


@dataclass(frozen=True)
class HADiscoveryConfig:
    prefix: str = "homeassistant"


@dataclass(frozen=True)
class HAAvailabilityConfig:
    per_entity_enabled: bool = True
    offline_after_seconds: int = 120


@dataclass(frozen=True)
class HAConfig:
    # "mqtt" => publish MQTT discovery/state to a downstream broker.
    # "native" => do NOT publish MQTT; keep in-memory state for consumers.
    transport: str = "mqtt"
    discovery: HADiscoveryConfig = field(default_factory=HADiscoveryConfig)
    state_prefix: str = "iotopen"
    publish_attributes: bool = True
    availability: HAAvailabilityConfig = field(default_factory=HAAvailabilityConfig)


@dataclass(frozen=True)
class SchedulerConfig:
    inventory_refresh_seconds: int = 60


@dataclass(frozen=True)
class HealthHttpConfig:
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass(frozen=True)
class AuthzConfig:
    # "disabled" | "monitor" | "enforce"
    mode: str = "disabled"

    # Explicit built-in prefixes (overrideable); defaulted from HA config in validate()
    allow_discovery_prefix: str = ""
    allow_state_prefix: str = ""

    allow_prefixes: list[str] = field(default_factory=list)
    allow_topics: list[str] = field(default_factory=list)
    deny_prefixes: list[str] = field(default_factory=list)

    auto_allow_topic_set: bool = True
    upstream_set_allow_prefixes: list[str] = field(default_factory=lambda: ["obj/generated", "obj"])


@dataclass(frozen=True)
class BridgeConfig:
    lynx: LynxConfig

    # Upstream MQTT (Lynx broker): subscribe to topic_read, publish to topic_set
    mqtt: MQTTConfig

    # Downstream MQTT (Home Assistant broker): publish discovery/state; receive HA /set commands
    # If omitted, defaults to `mqtt` (backward-compatible behavior).
    mqtt_downstream: MQTTConfig | None = None

    ha: HAConfig = field(default_factory=HAConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    health_http: HealthHttpConfig = field(default_factory=HealthHttpConfig)
    authz: AuthzConfig = field(default_factory=AuthzConfig)

    # Optional sidecar file for per-function mapping/capability overrides (YAML/JSON)
    mapping_path: str | None = None

    storage_path: str = "./state/iotopen-bridge.sqlite3"
    log_level: str = "INFO"
    raw_capture: RawCaptureConfig = field(default_factory=RawCaptureConfig)

    def validate(self) -> None:
        if not self.lynx.base_url:
            raise ConfigError("lynx.base_url is required")
        if not self.lynx.api_key:
            raise ConfigError("lynx.api_key is required")

        # If env var substitution did not happen, fail fast with a helpful message.
        if _ENV_VAR_RE.search(self.lynx.api_key) or re.search(
            r"%[A-Za-z0-9_]+%", str(self.lynx.api_key)
        ):
            raise ConfigError(
                "lynx.api_key looks like an unresolved environment placeholder. "
                "Set the env var (e.g. $env:LYNX_API_KEY=...) or put the API key directly in config.yaml."
            )

        if int(self.lynx.installation_id) <= 0:
            raise ConfigError("lynx.installation_id must be > 0")

        if not self.mqtt.host:
            raise ConfigError("mqtt.host (upstream) is required")

        if self.mqtt.password and (
            _ENV_VAR_RE.search(str(self.mqtt.password))
            or re.search(r"%[A-Za-z0-9_]+%", str(self.mqtt.password))
        ):
            raise ConfigError(
                "mqtt.password looks like an unresolved environment placeholder. "
                "Set the env var (e.g. $env:MQTT_PASSWORD=...) or put the password directly in config.yaml."
            )

        if not (1 <= int(self.mqtt.port) <= 65535):
            raise ConfigError("mqtt.port must be in 1..65535")

        # Validate HA transport.
        ha_transport = str(getattr(self.ha, "transport", "mqtt") or "mqtt").strip().lower()
        if ha_transport not in ("mqtt", "native"):
            raise ConfigError("ha.transport must be 'mqtt' or 'native'")

        # Backward compat: default downstream broker to upstream broker *only* when using MQTT transport.
        if ha_transport == "mqtt" and self.mqtt_downstream is None:
            object.__setattr__(self, "mqtt_downstream", self.mqtt)

        # Downstream broker validation (only relevant for MQTT transport).
        if ha_transport == "mqtt":
            # Ensure downstream client_id does not collide with upstream when same broker is used.
            down = self.mqtt_downstream or self.mqtt
            if (
                down.host == self.mqtt.host
                and int(down.port) == int(self.mqtt.port)
                and str(down.client_id) == str(self.mqtt.client_id)
            ):
                object.__setattr__(
                    self,
                    "mqtt_downstream",
                    MQTTConfig(
                        host=down.host,
                        port=int(down.port),
                        username=down.username,
                        password=down.password,
                        client_id=f"{down.client_id}-ha",
                        keepalive=int(down.keepalive),
                        tls=down.tls,
                    ),
                )
                down = self.mqtt_downstream or self.mqtt

            if not down.host:
                raise ConfigError("mqtt_downstream.host (downstream) is required")

            if down.password and (
                _ENV_VAR_RE.search(str(down.password))
                or re.search(r"%[A-Za-z0-9_]+%", str(down.password))
            ):
                raise ConfigError(
                    "mqtt_downstream.password looks like an unresolved environment placeholder. "
                    "Set the env var or put the password directly in config.yaml."
                )

            if not (1 <= int(down.port) <= 65535):
                raise ConfigError("mqtt_downstream.port must be in 1..65535")

        mode = str(self.authz.mode or "disabled").strip().lower()
        if mode not in {"disabled", "monitor", "enforce"}:
            raise ConfigError("authz.mode must be one of: disabled, monitor, enforce")

        allow_prefixes = _norm_prefixes(_as_list_str(self.authz.allow_prefixes))
        allow_topics = _as_list_str(self.authz.allow_topics)
        deny_prefixes = _norm_prefixes(_as_list_str(self.authz.deny_prefixes))
        upstream_set = _norm_prefixes(_as_list_str(self.authz.upstream_set_allow_prefixes))

        # Default allow_discovery_prefix/state_prefix from HA section if missing
        allow_discovery_prefix = _norm_prefix(self.authz.allow_discovery_prefix) or _norm_prefix(
            self.ha.discovery.prefix
        )
        allow_state_prefix = _norm_prefix(self.authz.allow_state_prefix) or _norm_prefix(
            self.ha.state_prefix
        )

        object.__setattr__(
            self,
            "authz",
            AuthzConfig(
                mode=mode,
                allow_discovery_prefix=allow_discovery_prefix,
                allow_state_prefix=allow_state_prefix,
                allow_prefixes=allow_prefixes,
                allow_topics=allow_topics,
                deny_prefixes=deny_prefixes,
                auto_allow_topic_set=bool(self.authz.auto_allow_topic_set),
                upstream_set_allow_prefixes=upstream_set or ["obj/generated", "obj"],
            ),
        )

    @classmethod
    def load(cls, path: str | None = None) -> BridgeConfig:
        p = str(path or "").strip()
        if not p:
            p = str(os.environ.get("IOTOPEN_BRIDGE_CONFIG", "")).strip()
        if not p:
            raise ConfigError("missing config path (and IOTOPEN_BRIDGE_CONFIG is not set)")
        return cls.from_file(p)

    @classmethod
    def from_file(cls, path: str) -> BridgeConfig:
        data = _expand_env(_load_any(path))
        if not isinstance(data, dict):
            raise ConfigError("config root must be a mapping/dict")

        # Resolve mapping_path relative to the config file directory (if provided).
        try:
            base_dir = Path(path).expanduser().resolve().parent
        except Exception:
            base_dir = Path(".")

        def _resolve_rel(v: Any) -> Any:
            if not isinstance(v, str):
                return v
            s = v.strip()
            if not s:
                return v
            p = Path(s).expanduser()
            if p.is_absolute():
                return str(p)
            return str((base_dir / p).resolve())

        # Accept mapping_path in either top-level or ha section
        if "mapping_path" in data:
            data["mapping_path"] = _resolve_rel(data.get("mapping_path"))
        ha_d = data.get("ha")
        if isinstance(ha_d, dict) and "mapping_path" in ha_d and "mapping_path" not in data:
            ha_d["mapping_path"] = _resolve_rel(ha_d.get("mapping_path"))

        return cls.from_mapping(data)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> BridgeConfig:
        try:
            lynx_d = dict(data["lynx"])
            mqtt_d = dict(data["mqtt"])
        except Exception as e:
            raise ConfigError("Config must contain top-level 'lynx' and 'mqtt' sections") from e

        tls_d_any = mqtt_d.get("tls") or {}
        tls_d = dict(tls_d_any) if isinstance(tls_d_any, dict) else {}
        tls = TLSConfig(**tls_d)

        # Downstream MQTT can be configured under several aliases (accept them all):
        # - mqtt_downstream (preferred)
        # - mqtt_ha / ha_mqtt
        # - ha: { mqtt: {...} }
        down_any = (
            data.get("mqtt_downstream")
            or data.get("mqtt_ha")
            or data.get("ha_mqtt")
            or (data.get("ha") or {}).get("mqtt")  # type: ignore[union-attr]
        )
        mqtt_downstream: MQTTConfig | None = None
        if isinstance(down_any, dict):
            down_d = dict(down_any)
            down_tls_any = down_d.get("tls") or {}
            down_tls_d = dict(down_tls_any) if isinstance(down_tls_any, dict) else {}
            down_tls = TLSConfig(**down_tls_d)
            if not str(down_d.get("host") or "").strip():
                raise ConfigError(
                    "mqtt_downstream.host is required when mqtt_downstream is provided"
                )
            mqtt_downstream = MQTTConfig(
                host=str(down_d["host"]),
                port=int(down_d.get("port", 1883)),
                username=down_d.get("username"),
                password=down_d.get("password"),
                client_id=str(down_d.get("client_id", "iotopen-bridge-ha")),
                keepalive=int(down_d.get("keepalive", 60)),
                tls=down_tls,
            )

        rc_any = data.get("raw_capture") or {}
        rc_d = dict(rc_any) if isinstance(rc_any, dict) else {}
        raw_capture = RawCaptureConfig(**rc_d)

        ha_d = data.get("ha") or {}
        ha_d = ha_d if isinstance(ha_d, dict) else {}
        ha_disc = ha_d.get("discovery") or {}
        ha_disc = ha_disc if isinstance(ha_disc, dict) else {}
        ha_av = ha_d.get("availability") or {}
        ha_av = ha_av if isinstance(ha_av, dict) else {}

        health_d = data.get("health_http") or {}
        health_d = health_d if isinstance(health_d, dict) else {}
        sched_d = data.get("scheduler") or {}
        sched_d = sched_d if isinstance(sched_d, dict) else {}

        authz_d = data.get("authz") or {}
        authz_d = authz_d if isinstance(authz_d, dict) else {}

        cfg = cls(
            lynx=LynxConfig(
                base_url=str(lynx_d["base_url"]),
                api_key=str(lynx_d["api_key"]),
                installation_id=int(lynx_d["installation_id"]),
            ),
            mqtt=MQTTConfig(
                host=str(mqtt_d["host"]),
                port=int(mqtt_d.get("port", 1883)),
                username=mqtt_d.get("username"),
                password=mqtt_d.get("password"),
                client_id=str(mqtt_d.get("client_id", "iotopen-bridge")),
                keepalive=int(mqtt_d.get("keepalive", 60)),
                tls=tls,
            ),
            mqtt_downstream=mqtt_downstream,
            ha=HAConfig(
                transport=str(ha_d.get("transport", "mqtt")),
                discovery=HADiscoveryConfig(prefix=str(ha_disc.get("prefix", "homeassistant"))),
                state_prefix=str(ha_d.get("state_prefix", "iotopen")),
                publish_attributes=bool(ha_d.get("publish_attributes", True)),
                availability=HAAvailabilityConfig(
                    per_entity_enabled=bool(ha_av.get("per_entity_enabled", True)),
                    offline_after_seconds=int(ha_av.get("offline_after_seconds", 120)),
                ),
            ),
            scheduler=SchedulerConfig(
                inventory_refresh_seconds=int(sched_d.get("inventory_refresh_seconds", 60)),
            ),
            health_http=HealthHttpConfig(
                enabled=bool(health_d.get("enabled", True)),
                host=str(health_d.get("host", "0.0.0.0")),
                port=int(health_d.get("port", 8080)),
            ),
            authz=AuthzConfig(
                mode=str(authz_d.get("mode", "disabled")),
                allow_discovery_prefix=str(authz_d.get("allow_discovery_prefix", "")),
                allow_state_prefix=str(authz_d.get("allow_state_prefix", "")),
                allow_prefixes=list(authz_d.get("allow_prefixes") or []),
                allow_topics=list(authz_d.get("allow_topics") or []),
                deny_prefixes=list(authz_d.get("deny_prefixes") or []),
                auto_allow_topic_set=bool(authz_d.get("auto_allow_topic_set", True)),
                upstream_set_allow_prefixes=list(authz_d.get("upstream_set_allow_prefixes") or []),
            ),
            mapping_path=(
                str(
                    data.get("mapping_path")
                    or (ha_d.get("mapping_path") if isinstance(ha_d, dict) else None)
                    or ""
                ).strip()
                or None
            ),
            storage_path=str(data.get("storage_path", "./state/iotopen-bridge.sqlite3")),
            log_level=str(data.get("log_level", "INFO")),
            raw_capture=raw_capture,
        )

        cfg.validate()
        return cfg
