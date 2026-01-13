# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/ha/facade.py
from __future__ import annotations

from typing import Any

from ..bridge.config import (
    AuthzConfig,
    BridgeConfig,
    HAAvailabilityConfig,
    HAConfig,
    HADiscoveryConfig,
    HealthHttpConfig,
    LynxConfig,
    MQTTConfig,
    SchedulerConfig,
    TLSConfig,
)
from ..bridge.runtime import BridgeRuntime


def _tls_from_flags(
    *,
    enabled: bool,
    cafile: str | None = None,
    verify_hostname: bool = True,
    insecure: bool = False,
    profile: str = "modern",
    client_cert: str | None = None,
    client_key: str | None = None,
) -> TLSConfig:
    return TLSConfig(
        enabled=bool(enabled),
        cafile=cafile,
        verify_hostname=bool(verify_hostname),
        insecure=bool(insecure),
        profile=str(profile or "modern"),
        client_cert=client_cert,
        client_key=client_key,
    )


def build_bridge_config(
    *,
    base_url: str,
    api_key: str,
    installation_id: int,
    # Upstream (Lynx broker) - legacy keys kept
    mqtt_host: str,
    mqtt_port: int = 1883,
    mqtt_username: str | None = None,
    mqtt_password: str | None = None,
    mqtt_client_id: str = "iotopen-bridge",
    mqtt_keepalive: int = 60,
    mqtt_tls: bool = False,
    mqtt_cafile: str | None = None,
    mqtt_verify_hostname: bool = True,
    mqtt_insecure: bool = False,
    # Downstream (HA broker) - new keys
    mqtt_downstream_host: str | None = None,
    mqtt_downstream_port: int | None = None,
    mqtt_downstream_username: str | None = None,
    mqtt_downstream_password: str | None = None,
    mqtt_downstream_client_id: str = "iotopen-bridge-ha",
    mqtt_downstream_keepalive: int = 60,
    mqtt_downstream_tls: bool | None = None,
    mqtt_downstream_cafile: str | None = None,
    mqtt_downstream_verify_hostname: bool | None = None,
    mqtt_downstream_insecure: bool | None = None,
    # Alias names some HA code prefers
    ha_mqtt_host: str | None = None,
    ha_mqtt_port: int | None = None,
    ha_mqtt_username: str | None = None,
    ha_mqtt_password: str | None = None,
    ha_mqtt_tls: bool | None = None,
    ha_mqtt_verify_hostname: bool | None = None,
    ha_mqtt_insecure: bool | None = None,
    ha_mqtt_client_id: str | None = None,
    # HA discovery/state
    ha_transport: str = "mqtt",
    discovery_prefix: str = "homeassistant",
    state_prefix: str = "iotopen",
    publish_attributes: bool = True,
    per_entity_availability: bool = True,
    offline_after_seconds: int = 120,
    # runtime
    inventory_refresh_seconds: int = 60,
    health_http_enabled: bool = True,
    health_http_host: str = "0.0.0.0",
    health_http_port: int = 8080,
    storage_path: str = "./state/iotopen-bridge.sqlite3",
    log_level: str = "INFO",
    authz_mode: str = "disabled",
    **_: Any,
) -> BridgeConfig:
    # Resolve downstream from either mqtt_downstream_* or ha_mqtt_*
    dh = mqtt_downstream_host or ha_mqtt_host
    dp = mqtt_downstream_port if mqtt_downstream_port is not None else ha_mqtt_port
    du = mqtt_downstream_username if mqtt_downstream_username is not None else ha_mqtt_username
    dpass = mqtt_downstream_password if mqtt_downstream_password is not None else ha_mqtt_password
    dcid = mqtt_downstream_client_id
    if ha_mqtt_client_id:
        dcid = ha_mqtt_client_id
    dka = mqtt_downstream_keepalive
    if dp is None:
        dp = 1883

    dtls_enabled = mqtt_downstream_tls
    if dtls_enabled is None:
        dtls_enabled = ha_mqtt_tls
    if dtls_enabled is None:
        # default downstream TLS to False unless explicitly set
        dtls_enabled = False

    d_verify = mqtt_downstream_verify_hostname
    if d_verify is None:
        d_verify = ha_mqtt_verify_hostname
    if d_verify is None:
        d_verify = True

    d_insecure = mqtt_downstream_insecure
    if d_insecure is None:
        d_insecure = ha_mqtt_insecure
    if d_insecure is None:
        d_insecure = False

    cfg = BridgeConfig(
        lynx=LynxConfig(
            base_url=str(base_url), api_key=str(api_key), installation_id=int(installation_id)
        ),
        mqtt=MQTTConfig(
            host=str(mqtt_host),
            port=int(mqtt_port),
            username=mqtt_username,
            password=mqtt_password,
            client_id=str(mqtt_client_id),
            keepalive=int(mqtt_keepalive),
            tls=_tls_from_flags(
                enabled=bool(mqtt_tls),
                cafile=mqtt_cafile,
                verify_hostname=bool(mqtt_verify_hostname),
                insecure=bool(mqtt_insecure),
            ),
        ),
        mqtt_downstream=(
            MQTTConfig(
                host=str(dh),
                port=int(dp),
                username=du,
                password=dpass,
                client_id=str(dcid),
                keepalive=int(dka),
                tls=_tls_from_flags(
                    enabled=bool(dtls_enabled),
                    cafile=mqtt_downstream_cafile,
                    verify_hostname=bool(d_verify),
                    insecure=bool(d_insecure),
                ),
            )
            if dh
            else None
        ),
        ha=HAConfig(
            transport=str(ha_transport),
            discovery=HADiscoveryConfig(prefix=str(discovery_prefix)),
            state_prefix=str(state_prefix),
            publish_attributes=bool(publish_attributes),
            availability=HAAvailabilityConfig(
                per_entity_enabled=bool(per_entity_availability),
                offline_after_seconds=int(offline_after_seconds),
            ),
        ),
        scheduler=SchedulerConfig(inventory_refresh_seconds=int(inventory_refresh_seconds)),
        health_http=HealthHttpConfig(
            enabled=bool(health_http_enabled),
            host=str(health_http_host),
            port=int(health_http_port),
        ),
        authz=AuthzConfig(mode=str(authz_mode)),
        storage_path=str(storage_path),
        log_level=str(log_level),
    )
    cfg.validate()
    return cfg


class HABridgeHandle:
    """Thin handle for HA custom components. Runs BridgeRuntime synchronously (thread-safe)."""

    def __init__(self, runtime: BridgeRuntime) -> None:
        self._rt = runtime

    @classmethod
    def from_config(cls, cfg: BridgeConfig) -> HABridgeHandle:
        return cls(BridgeRuntime(cfg=cfg))

    # Sync lifecycle (for CLI/tests)
    def start(self) -> None:
        self._rt.start()

    def stop(self) -> None:
        self._rt.stop()

    # Async lifecycle (for HA)
    async def async_start(self, hass: Any) -> None:
        # We accept hass for API-compat; BridgeRuntime itself is not tied to hass.
        await hass.async_add_executor_job(self._rt.start)

    async def async_stop(self, hass: Any) -> None:
        await hass.async_add_executor_job(self._rt.stop)

    @property
    def runtime(self) -> BridgeRuntime:
        return self._rt
