# File: src/iotopen_bridge/core/config_base.py
# SPDX-License-Identifier: Apache-2.0

"""Lightweight configuration helpers.

Thin layer that:
  - loads yaml/json/toml to a dict
  - expands ${ENV_VAR} in strings (recursively)
  - provides a dataclass-friendly base class

Concrete configs (e.g., BridgeConfig) can subclass ConfigBase and implement
additional validation.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, TypeVar, overload

import yaml

from .errors import ConfigError
from .typing import StrPath

T = TypeVar("T", bound="ConfigBase")

_ENV_VAR_RE = re.compile(r"\$\{([A-Z0-9_]+)\}")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e
    except OSError as e:
        raise ConfigError(f"Could not read config file: {path} ({e})") from e


@overload
def expand_env(value: str) -> str: ...
@overload
def expand_env(value: list[Any]) -> list[Any]: ...
@overload
def expand_env(value: dict[str, Any]) -> dict[str, Any]: ...
@overload
def expand_env(value: Any) -> Any: ...


def expand_env(value: Any) -> Any:
    """Recursively expand ${VARNAME} placeholders in strings."""
    if isinstance(value, str):

        def repl(m: re.Match[str]) -> str:
            key = m.group(1)
            return os.environ.get(key, m.group(0))

        return _ENV_VAR_RE.sub(repl, value)

    if isinstance(value, dict):
        return {k: expand_env(v) for k, v in value.items()}

    if isinstance(value, list):
        return [expand_env(v) for v in value]

    return value


def load_mapping(path: StrPath) -> dict[str, Any]:
    p = Path(path)
    suffix = p.suffix.lower()
    raw = _read_text(p)

    if suffix in {".yml", ".yaml"}:
        data: Any = yaml.safe_load(raw) or {}
    elif suffix == ".json":
        data = json.loads(raw)
    elif suffix == ".toml":
        # mypy may run with python_version < 3.11 even if runtime is 3.13,
        # so tomllib might be "missing" in typeshed for that config.
        try:
            import tomllib as _toml  # type: ignore[import-not-found]
        except Exception:
            import tomli as _toml  # type: ignore[import-not-found]

        data = _toml.loads(raw)
    else:
        raise ConfigError(f"Unsupported config format: {p.name} (expected .yml/.yaml/.json/.toml)")

    if not isinstance(data, dict):
        raise ConfigError("Config root must be a mapping/object")

    expanded = expand_env(data)
    if not isinstance(expanded, dict):
        raise ConfigError("Config root must be a mapping/object")
    return expanded


class ConfigBase:
    """Base class for config dataclasses (optional)."""

    @classmethod
    def from_mapping(cls: type[T], data: Mapping[str, Any]) -> T:
        try:
            return cls(**dict(data))  # type: ignore[misc]
        except TypeError as e:
            raise ConfigError(f"Invalid config fields for {cls.__name__}: {e}") from e

    @classmethod
    def load(cls: type[T], path: StrPath) -> T:
        return cls.from_mapping(load_mapping(path))

    def to_dict(self) -> dict[str, Any]:
        if is_dataclass(self):
            return asdict(self)
        raise TypeError("to_dict() requires a dataclass config instance")
