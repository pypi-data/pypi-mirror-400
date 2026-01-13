import re
from collections.abc import Mapping
from typing import Any

_SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "token",
    "authorization",
    "password",
    "passwd",
    "secret",
    "private_key",
    "client_key",
}
_BEARER_RE = re.compile(r"(?i)\b(bearer)\s+([a-z0-9\-\._~\+\/]+=*)")


def scrub(obj: Any) -> Any:
    if isinstance(obj, Mapping):
        out = {}
        for k, v in obj.items():
            if str(k).lower() in _SENSITIVE_KEYS:
                out[k] = "***"
            else:
                out[k] = scrub(v)
        return out
    if isinstance(obj, (list, tuple)):
        return [scrub(x) for x in obj]
    if isinstance(obj, str):
        if _BEARER_RE.search(obj):
            return _BEARER_RE.sub(lambda m: f"{m.group(1)} ***(redacted)***", obj)
        return obj
    return obj
