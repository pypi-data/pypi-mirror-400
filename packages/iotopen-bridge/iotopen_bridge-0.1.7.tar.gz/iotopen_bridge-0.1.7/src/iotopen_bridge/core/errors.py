# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/core/errors.py
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass


class BridgeError(Exception):
    """Base exception for iotopen-bridge."""


class ConfigError(BridgeError):
    """Invalid/unsupported configuration."""


class LifecycleError(BridgeError):
    """Invalid lifecycle state or operation."""


class LynxError(BridgeError):
    """Errors talking to Lynx API."""


class NotFoundError(BridgeError):
    """A required resource was not found."""


class StorageError(BridgeError):
    """Persistence/storage layer errors."""


class DecodeError(BridgeError):
    """Generic decode/parse errors outside payload/decoders."""


class PolicyDenied(BridgeError):
    """Raised when a security policy blocks an action (publish/subscribe/etc.)."""


@dataclass(frozen=True)
class AggregateError(BridgeError):
    """Represent multiple errors as one exception.

    Useful when you want to validate many things and report all failures at once.
    """

    message: str
    errors: Sequence[BaseException]

    def __str__(self) -> str:
        head = self.message or "Multiple errors"
        if not self.errors:
            return head
        lines = [head]
        for i, e in enumerate(self.errors, start=1):
            lines.append(f"  {i}. {type(e).__name__}: {e}")
        return "\n".join(lines)

    @classmethod
    def from_iterable(cls, message: str, errors: Iterable[BaseException]) -> AggregateError:
        return cls(message=str(message), errors=tuple(errors))


class ValidationError(BridgeError):
    """Raised when validation fails."""

    def __init__(self, message: str, *, field: str | None = None) -> None:
        self.field = field
        super().__init__(message if field is None else f"{field}: {message}")
