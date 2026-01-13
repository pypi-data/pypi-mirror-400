from dataclasses import dataclass, field
from typing import Any

from .entrypoints import load_entrypoint_group


@dataclass
class PluginRegistry:
    mappers: list[Any] = field(default_factory=list)

    def load(self) -> None:
        self.mappers.extend(load_entrypoint_group("iotopen_bridge.mappers"))
