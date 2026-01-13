from collections.abc import Mapping
from typing import Any, Protocol


class HttpClient(Protocol):
    async def get_json(
        self, url: str, headers: Mapping[str, str], timeout: float = 15.0
    ) -> Any: ...
