from typing import Protocol

from ..models.ha import HaEntitySpec
from ..models.lynx import FunctionX


class MapperPlugin(Protocol):
    def can_handle(self, fx: FunctionX) -> bool: ...
    def map_entity(self, fx: FunctionX) -> HaEntitySpec: ...
