from typing import Protocol


class SecretProvider(Protocol):
    def get(self, key: str) -> str | None: ...
