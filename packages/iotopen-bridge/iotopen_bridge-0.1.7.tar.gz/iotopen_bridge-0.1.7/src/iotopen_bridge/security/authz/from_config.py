# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/authz/from_config.py
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .policy import PolicyEngine
from .rules import AuthzRules


@dataclass(frozen=True)
class PolicyBundle:
    """Convenience bundle used by runtime composition."""

    rules: AuthzRules
    policy: PolicyEngine


def _as_list_str(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        out: list[str] = []
        for x in v:
            s = str(x or "").strip()
            if s:
                out.append(s)
        return out
    s = str(v or "").strip()
    return [s] if s else []


def _get(d: Mapping[str, Any], key: str, default: Any = None) -> Any:
    try:
        return d.get(key, default)
    except Exception:
        return default


def build_policy_engine(authz_cfg: Any) -> PolicyEngine:
    """
    Build PolicyEngine(AuthzRules, mode) from either:
      - dict-like config (as in your example snippet)
      - BridgeConfig.authz (dataclass) that has fields like mode/allow_prefixes/deny_prefixes
    Note: This builder does NOT guess discovery/state prefixes unless provided.
    Use build_policy_bundle(...) if you want the runtime-level defaults.
    """
    if isinstance(authz_cfg, Mapping):
        mode = _get(authz_cfg, "mode", "disabled")
        rules = AuthzRules(
            allow_discovery_prefix=str(_get(authz_cfg, "allow_discovery_prefix", "")),
            allow_state_prefix=str(_get(authz_cfg, "allow_state_prefix", "")),
        )
        for p in _as_list_str(_get(authz_cfg, "allow_prefixes", [])):
            rules.allow_prefix(p)
        for t in _as_list_str(_get(authz_cfg, "allow_topics", [])):
            rules.allow_topic(t)
        for p in _as_list_str(_get(authz_cfg, "deny_prefixes", [])):
            rules.deny_prefix(p)

        return PolicyEngine(rules=rules, mode=mode)

    # Dataclass-ish: BridgeConfig.authz
    mode = getattr(authz_cfg, "mode", "disabled")
    rules = AuthzRules(
        allow_discovery_prefix=str(getattr(authz_cfg, "allow_discovery_prefix", "")),
        allow_state_prefix=str(getattr(authz_cfg, "allow_state_prefix", "")),
    )
    for p in _as_list_str(getattr(authz_cfg, "allow_prefixes", [])):
        rules.allow_prefix(p)
    for t in _as_list_str(getattr(authz_cfg, "allow_topics", [])):
        rules.allow_topic(t)
    for p in _as_list_str(getattr(authz_cfg, "deny_prefixes", [])):
        rules.deny_prefix(p)

    return PolicyEngine(rules=rules, mode=mode)


def build_policy_bundle(
    *,
    mode: Any,
    allow_discovery_prefix: str,
    allow_state_prefix: str,
    allow_prefixes: Sequence[str] | None = None,
    allow_topics: Sequence[str] | None = None,
    deny_prefixes: Sequence[str] | None = None,
) -> PolicyBundle:
    """Runtime composition helper: you pass the HA discovery/state prefixes explicitly."""
    rules = AuthzRules(
        allow_discovery_prefix=str(allow_discovery_prefix or ""),
        allow_state_prefix=str(allow_state_prefix or ""),
    )

    for p in _as_list_str(list(allow_prefixes or [])):
        rules.allow_prefix(p)
    for t in _as_list_str(list(allow_topics or [])):
        rules.allow_topic(t)
    for p in _as_list_str(list(deny_prefixes or [])):
        rules.deny_prefix(p)

    policy = PolicyEngine(rules=rules, mode=mode)
    return PolicyBundle(rules=rules, policy=policy)


def build_policy_bundle_from_bridge_config(cfg: Any) -> PolicyBundle:
    """
    Optional helper if you want a single call in BridgeRuntime.__post_init__.
    Expects:
      cfg.ha.discovery.prefix
      cfg.ha.state_prefix
      cfg.authz.mode / allow_prefixes / allow_topics / deny_prefixes
    """
    allow_discovery_prefix = str(cfg.ha.discovery.prefix)
    allow_state_prefix = str(cfg.ha.state_prefix)
    authz = cfg.authz

    return build_policy_bundle(
        mode=getattr(authz, "mode", "disabled"),
        allow_discovery_prefix=allow_discovery_prefix,
        allow_state_prefix=allow_state_prefix,
        allow_prefixes=getattr(authz, "allow_prefixes", []),
        allow_topics=getattr(authz, "allow_topics", []),
        deny_prefixes=getattr(authz, "deny_prefixes", []),
    )
