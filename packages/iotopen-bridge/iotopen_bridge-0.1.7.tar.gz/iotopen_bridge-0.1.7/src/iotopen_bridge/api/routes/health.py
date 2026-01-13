from __future__ import annotations

from typing import Any


def register(app: Any, deps: Any) -> None:
    """
    Registers:
      - GET /healthz
      - GET /readyz
      - GET /metrics

    `app` is FastAPI instance, `deps.health` is bridge Health model.
    """
    health = deps.health

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        return {
            "status": "ok",
            "mqtt_connected": bool(getattr(health, "mqtt_connected", False)),
            "last_inventory_ok": bool(getattr(health, "last_inventory_ok", False)),
            "last_inventory_ts": getattr(health, "last_inventory_ts", None),
            "last_error": getattr(health, "last_error", None),
        }

    @app.get("/readyz")
    def readyz() -> tuple[dict[str, Any], int]:
        mqtt_ok = bool(getattr(health, "mqtt_connected", False))
        inv_ok = bool(getattr(health, "last_inventory_ok", False))
        payload = {
            "status": "ready" if (mqtt_ok and inv_ok) else "not_ready",
            "mqtt_connected": mqtt_ok,
            "last_inventory_ok": inv_ok,
            "last_inventory_ts": getattr(health, "last_inventory_ts", None),
            "last_error": getattr(health, "last_error", None),
        }
        return payload, (200 if (mqtt_ok and inv_ok) else 503)

    @app.get("/metrics")
    def metrics() -> Any:
        # Prometheus exposition format
        try:
            from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY  # type: ignore
            from prometheus_client.exposition import generate_latest  # type: ignore
        except Exception:
            # if fastapi isn't present the API isn't running anyway; but keep explicit
            return (
                "prometheus_client not installed\n",
                501,
                {"Content-Type": "text/plain; charset=utf-8"},
            )

        data = generate_latest(REGISTRY)
        return (data, 200, {"Content-Type": str(CONTENT_TYPE_LATEST)})
