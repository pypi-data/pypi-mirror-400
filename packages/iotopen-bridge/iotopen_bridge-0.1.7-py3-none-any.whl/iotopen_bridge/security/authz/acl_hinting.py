from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class AclHint:
    username: str
    lines: list[str]


def render_mosquitto_acl(
    username: str, allow_prefixes: Iterable[str], discovery_prefix: str, state_prefix: str
) -> AclHint:
    lines = [
        f"user {username}",
        f"topic readwrite {discovery_prefix}/#",
        f"topic readwrite {state_prefix}/#",
    ]
    for p in allow_prefixes:
        p = p.rstrip("#")
        lines.append(f"topic readwrite {p}#")
    return AclHint(username=username, lines=lines)
