# iotopen-bridge

Secure, extensible bridge between **IoT Open Lynx** and **Home Assistant** using MQTT + HA MQTT Discovery.

## Quick start

### Install (PyPI)
```bash
pip install iotopen-bridge
```

### Install (dev)
```bash
pip install -e ".[dev]"
```


### Home Assistant integration helper (optional)

If you are writing a Home Assistant custom integration and want **minimal glue code**,
you can build a `BridgeConfig` from your config flow values and start the runtime from HA:

```python
from iotopen_bridge.ha import HABridgeHandle, build_bridge_config

cfg = build_bridge_config(
    base_url="https://lynx.iotopen.se",
    api_key="...",
    installation_id=2222,
    mqtt_host="localhost",
    mqtt_port=1883,
)

handle = HABridgeHandle.from_config(cfg)
await handle.async_start(hass)
```

### Configure
Create `config.yml` (see `examples/config.example.yaml`):

```yaml
lynx:
  base_url: "https://lynx.example"
  installation_id: 2222
  api_key: "${IOTOPEN_API_KEY}"

mqtt:
  host: "mqtt.example"
  port: 8883 #tls 1883 non secured 
  username: "${MQTT_USER}"
  password: "${MQTT_PASS}"
  client_id: "iotopen-bridge"
  tls:
    enabled: true
    cafile: "/etc/ssl/certs/ca-certificates.crt"
    verify_hostname: true

ha:
  discovery:
    enabled: true
    prefix: "homeassistant"
  state_prefix: "iotopen"
```

### Run
```bash
iotopen-bridge run --config config.yml
```

### Probes
```bash
iotopen-bridge probe-api --config config.yml
iotopen-bridge probe-mqtt --config config.yml --sub "2086/obj/#" --count 20
```

## Design
- Inventory from Lynx API (FunctionX).
- Telemetry from FunctionX `topic_read`.
- Commands to FunctionX `topic_set`.
- HA MQTT Discovery auto-creates entities in Home Assistant.

See `docs/architecture.md`.
