# File: src/iotopen_bridge/lynx/client.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import random
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urljoin

import requests

from ..core.errors import LynxError
from .auth import LynxAuth

_LOGGER = logging.getLogger(__name__)

# Transient-ish HTTP statuses where retry is usually safe for GETs.
_DEFAULT_RETRY_STATUSES: tuple[int, ...] = (408, 425, 429, 500, 502, 503, 504)


class LynxHttpError(LynxError):
    """HTTP error with status_code attached (still a LynxError for compatibility)."""

    def __init__(self, message: str, *, status_code: int) -> None:
        super().__init__(message)
        self.status_code = int(status_code)


def _sleep_backoff(attempt: int, *, base: float = 0.4, cap: float = 6.0) -> None:
    """Exponential backoff with jitter."""
    t = min(cap, base * (2**attempt))
    jitter = t * 0.25
    time.sleep(max(0.0, t + random.uniform(-jitter, jitter)))


def _try_int(v: Any) -> int | None:
    try:
        if v is None:
            return None
        return int(v)
    except Exception:
        return None


def _parse_retry_after_seconds(value: str | None) -> float | None:
    """Parse Retry-After per HTTP semantics: delta-seconds or HTTP-date."""
    if not value:
        return None
    s = value.strip()
    if not s:
        return None

    # delta-seconds
    n = _try_int(s)
    if n is not None:
        return float(n) if n >= 0 else None

    # HTTP-date
    try:
        dt = parsedate_to_datetime(s)
        if dt is None:
            return None
        now = time.time()
        ts = dt.timestamp()
        return max(0.0, float(ts - now))
    except Exception:
        return None


def _is_json_content_type(content_type: str | None) -> bool:
    if not content_type:
        return False
    ct = content_type.lower()
    return "application/json" in ct or ct.endswith("+json")


def _safe_snippet(text: str, limit: int = 800) -> str:
    t = (text or "").strip()
    return t if len(t) <= limit else (t[:limit] + "…")


def _extract_items(payload: Any) -> list[dict[str, Any]]:
    """Normalize common API response shapes to list[dict]."""
    if isinstance(payload, list):
        return [dict(x) for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for k in ("items", "data", "results"):
            v = payload.get(k)
            if isinstance(v, list):
                return [dict(x) for x in v if isinstance(x, dict)]
    return []


@dataclass
class LynxApiClient:
    """Robust REST client for the IoT Open Lynx API (requests-based).

    FunctionX listing endpoint varies by deployment.

    We auto-detect (and cache) which FunctionX endpoint works.
    We prefer the documented v2 endpoint first and only fall back to legacy
    paths when necessary.
    """

    base_url: str
    auth: LynxAuth

    timeout: float | tuple[float, float] = (5.0, 20.0)

    max_retries: int = 4
    retry_statuses: tuple[int, ...] = _DEFAULT_RETRY_STATUSES

    _session: requests.Session = field(default_factory=requests.Session, init=False, repr=False)

    # Cache: once we find a working endpoint style, reuse it.
    _fx_endpoint: tuple[str, dict[str, Any] | None] | None = field(
        default=None, init=False, repr=False
    )

    def __post_init__(self) -> None:
        self.base_url = str(self.base_url or "").strip()
        if not self.base_url:
            raise LynxError("LynxApiClient.base_url is required")

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self._session.close()

    def __enter__(self) -> LynxApiClient:
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        self.close()

    def _url(self, path: str) -> str:
        return urljoin(self.base_url.rstrip("/") + "/", str(path).lstrip("/"))

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "User-Agent": "iotopen-bridge/1.0",
            **self.auth.headers(),
        }

    def _format_http_error(self, url: str, resp: requests.Response) -> str:
        status = int(resp.status_code)

        snippet = ""
        try:
            ct = resp.headers.get("Content-Type")
            if _is_json_content_type(ct):
                try:
                    snippet = _safe_snippet(json.dumps(resp.json(), ensure_ascii=False))
                except Exception:
                    snippet = _safe_snippet(resp.text)
            else:
                snippet = _safe_snippet(resp.text)
        except Exception:
            snippet = ""

        if status in (401, 403):
            return f"HTTP {status} from {url}: authorization failed. {snippet}"

        return f"HTTP {status} from {url}: {snippet}"

    def _parse_response(self, resp: requests.Response) -> Any:
        if resp.status_code == 204:
            return None

        ct = resp.headers.get("Content-Type")
        if _is_json_content_type(ct):
            return resp.json()

        # Gateways sometimes return JSON with wrong content-type; try json then text.
        try:
            return resp.json()
        except Exception:
            txt = resp.text
            try:
                return json.loads(txt)
            except Exception:
                return txt

    def _should_retry(self, method: str, status_code: int) -> bool:
        m = method.upper()
        if m not in {"GET", "HEAD", "OPTIONS"}:
            return False
        return status_code in self.retry_statuses

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
    ) -> Any:
        url = self._url(path)
        headers = self._headers()
        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                resp = self._session.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=dict(params) if params else None,
                    json=json_body,
                    timeout=self.timeout,
                )

                if resp.status_code >= 400:
                    status = int(resp.status_code)

                    if attempt < self.max_retries and self._should_retry(method, status):
                        ra = _parse_retry_after_seconds(resp.headers.get("Retry-After"))
                        if ra is not None and ra <= 60.0:
                            _LOGGER.debug("Retry-After=%ss for %s %s", ra, method, url)
                            time.sleep(float(ra))
                        else:
                            _sleep_backoff(attempt)
                        continue

                    raise LynxHttpError(self._format_http_error(url, resp), status_code=status)

                return self._parse_response(resp)

            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt >= self.max_retries:
                    break
                _sleep_backoff(attempt)
            except LynxHttpError:
                raise
            except LynxError:
                raise
            except Exception as e:
                last_exc = e
                if attempt >= self.max_retries:
                    break
                _sleep_backoff(attempt)

        raise LynxError(f"{method.upper()} failed for {url}: {last_exc}") from last_exc

    def _get(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    # -------------------------
    # FunctionX endpoint discovery
    # -------------------------

    def _functionx_candidates(
        self, installation_id: int
    ) -> Sequence[tuple[str, dict[str, Any] | None]]:
        iid = int(installation_id)
        # Candidate order is important: prefer the documented endpoint first.
        return (
            (f"/api/v2/functionx/{iid}", None),
            ("/api/v1/functionx", {"installationId": iid}),
            ("/api/functionx", {"installationId": iid}),
            # Legacy / internal variants (some deployments expose these).
            (f"/api/vw/functionx/{iid}", None),
            ("/api/vw/functionx", {"installationId": iid}),
        )

    def _probe_functionx_endpoint(self, installation_id: int) -> tuple[str, dict[str, Any] | None]:
        last_404: Exception | None = None
        last_auth: Exception | None = None

        for path, params in self._functionx_candidates(installation_id):
            try:
                payload = self._get(path, params=params)
                items = _extract_items(payload)
                # If we got a valid shape (even empty list), treat it as success.
                if isinstance(payload, (list, dict)) and items is not None:
                    _LOGGER.info("Using FunctionX endpoint: %s (params=%s)", path, bool(params))
                    return (path, params)
            except LynxHttpError as e:
                code = getattr(e, "status_code", None)
                if code == 404:
                    last_404 = e
                    continue
                # Some endpoints exist but require different auth schemes.
                # Keep probing other candidates before failing.
                if code in (401, 403):
                    last_auth = last_auth or e
                    continue
                raise

        # If everything was 404, raise the last one (best signal).
        if last_404 is not None:
            raise last_404

        # If everything looked like auth failures, surface the last one.
        if last_auth is not None:
            raise last_auth

        raise LynxError("Could not detect a working FunctionX endpoint (no candidates succeeded).")

    # -------------------------
    # Public API
    # -------------------------

    def list_functions(self, installation_id: int) -> list[dict[str, Any]]:
        """Return raw FunctionX dicts from Lynx."""
        iid = int(installation_id)

        if self._fx_endpoint is None:
            self._fx_endpoint = self._probe_functionx_endpoint(iid)

        path, params = self._fx_endpoint
        payload = self._get(path, params=params)
        return _extract_items(payload)

    async def list_functionx(self, installation_id: int) -> list[dict[str, Any]]:
        """Async wrapper to avoid blocking the event loop."""
        return await asyncio.to_thread(self.list_functions, int(installation_id))

    def list_functionx_sync(self, installation_id: int) -> list[dict[str, Any]]:
        return self.list_functions(int(installation_id))
