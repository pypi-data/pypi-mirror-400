# File: src/iotopen_bridge/core/result.py
# SPDX-License-Identifier: Apache-2.0

"""Tiny Result type used for internal operations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Result(Generic[T]):
    value: T | None = None
    error: str | None = None

    @staticmethod
    def success(value: T) -> Result[T]:
        return Result(value=value, error=None)

    @staticmethod
    def failure(error: str) -> Result[T]:
        return Result(value=None, error=str(error))

    @property
    def ok(self) -> bool:
        return self.error is None

    def map(self, fn: Callable[[T], T]) -> Result[T]:
        if not self.ok or self.value is None:
            return self
        try:
            return Result.success(fn(self.value))
        except Exception as e:
            return Result.failure(str(e))
