# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/security/authz/rules.py
from __future__ import annotations

import threading
from collections.abc import Iterable
from dataclasses import dataclass, field

from ...core.errors import PolicyDenied


def _norm_prefix(p: str) -> str:
    """Normalize a prefix (no leading '/', trimmed, no trailing '/')."""
    p = str(p or "").strip()
    if not p:
        return ""
    if p.startswith("/"):
        p = p[1:]
    while p.endswith("/"):
        p = p[:-1]
    return p


def _norm_topic(t: str) -> str:
    """Normalize a topic or topic filter (no leading '/', trimmed)."""
    t = str(t or "").strip()
    if t.startswith("/"):
        t = t[1:]
    return t


def _has_wildcards(t: str) -> bool:
    return ("+" in t) or ("#" in t)


def _fixed_prefix_before_wildcard(topic_filter: str) -> str:
    """Return the stable prefix before the first wildcard segment."""
    tf = _norm_topic(topic_filter)
    if not tf:
        return ""

    parts = [p for p in tf.split("/") if p != ""]
    fixed: list[str] = []
    for seg in parts:
        if seg in {"+", "#"}:
            break
        if ("+" in seg) or ("#" in seg):
            break
        fixed.append(seg)

    return "/".join(fixed)


def _is_under(child: str, parent: str) -> bool:
    """True if child == parent OR child is within parent subtree."""
    if not parent:
        return False
    return child == parent or child.startswith(parent + "/")


@dataclass
class AuthzRules:
    """Authorization rules for MQTT topic access.

    Design goals:
      - publish requires a concrete Topic Name (no '+' or '#')
      - subscribe accepts Topic Filters but must not broaden permissions
      - deny prefixes win, including when a filter would include a denied subtree
      - deny ALWAYS wins, even inside built-in state/discovery prefixes
    """

    allow_discovery_prefix: str
    allow_state_prefix: str

    allow_topic_prefixes: set[str] = field(default_factory=set)
    allow_topics_set: set[str] = field(default_factory=set)
    deny_topic_prefixes: set[str] = field(default_factory=set)

    _lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)

    def allow_prefix(self, prefix: str) -> bool:
        p = _norm_prefix(prefix)
        if not p:
            return False
        with self._lock:
            if p in self.allow_topic_prefixes:
                return False
            self.allow_topic_prefixes.add(p)
            return True

    def deny_prefix(self, prefix: str) -> bool:
        p = _norm_prefix(prefix)
        if not p:
            return False
        with self._lock:
            if p in self.deny_topic_prefixes:
                return False
            self.deny_topic_prefixes.add(p)
            return True

    def allow_topic(self, topic: str) -> bool:
        t = _norm_topic(topic)
        if not t:
            return False
        with self._lock:
            if t in self.allow_topics_set:
                return False
            self.allow_topics_set.add(t)
            return True

    def allow_topics(self, topics: Iterable[str]) -> int:
        n = 0
        for t in topics:
            if self.allow_topic(t):
                n += 1
        return n

    def is_allowed_topic(self, topic: str) -> bool:
        """Check a *concrete* topic (Topic Name)."""
        t = _norm_topic(topic)
        if not t:
            return False

        disc = _norm_prefix(self.allow_discovery_prefix)
        state = _norm_prefix(self.allow_state_prefix)

        with self._lock:
            deny = tuple(self.deny_topic_prefixes)
            allow_prefixes = tuple(self.allow_topic_prefixes)
            allow_topics = tuple(self.allow_topics_set)

        # ✅ DENY ALWAYS WINS (even within built-ins)
        for dp in deny:
            if _is_under(t, dp):
                return False

        # Built-ins (allowed unless denied)
        if disc and _is_under(t, disc):
            return True
        if state and _is_under(t, state):
            return True

        # Exact allow
        if t in allow_topics:
            return True

        # Prefix allow
        return any(_is_under(t, ap) for ap in allow_prefixes)

    def is_allowed_filter(self, topic_filter: str) -> bool:
        """Check a SUBSCRIBE filter (Topic Filter, may contain wildcards)."""
        tf = _norm_topic(topic_filter)
        if not tf:
            return False

        if not _has_wildcards(tf):
            return self.is_allowed_topic(tf)

        fixed = _fixed_prefix_before_wildcard(tf)
        if not fixed:
            return False

        disc = _norm_prefix(self.allow_discovery_prefix)
        state = _norm_prefix(self.allow_state_prefix)

        with self._lock:
            deny = tuple(self.deny_topic_prefixes)
            allow_prefixes = tuple(self.allow_topic_prefixes)

        # Deny wins in both directions:
        for dp in deny:
            if _is_under(fixed, dp) or _is_under(dp, fixed):
                return False

        # Built-in prefixes: only allow if the filter is within them
        if disc and _is_under(fixed, disc):
            return True
        if state and _is_under(fixed, state):
            return True

        # Allow prefixes: only allow if filter is within an allowed prefix
        return any(_is_under(fixed, ap) for ap in allow_prefixes)

    def require_publish(self, topic: str) -> None:
        t = _norm_topic(topic)
        if not t:
            raise PolicyDenied("publish topic is empty")
        if _has_wildcards(t):
            raise PolicyDenied(f"publish topic must be concrete (no wildcards): {t!r}")
        if not self.is_allowed_topic(t):
            raise PolicyDenied(f"publish denied for topic: {t!r}")

    def require_subscribe(self, topic_filter: str) -> None:
        tf = _norm_topic(topic_filter)
        if not tf:
            raise PolicyDenied("subscribe filter is empty")
        if not self.is_allowed_filter(tf):
            raise PolicyDenied(f"subscribe denied for filter: {tf!r}")
