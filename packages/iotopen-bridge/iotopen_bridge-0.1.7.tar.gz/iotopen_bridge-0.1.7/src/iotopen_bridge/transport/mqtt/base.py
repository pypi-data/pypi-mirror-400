from collections.abc import Callable
from typing import Protocol

MessageHandler = Callable[[str, bytes, int, bool], None]
ConnectHandler = Callable[[bool, str], None]


class IMqttClient(Protocol):
    def connect(self) -> None: ...
    def disconnect(self) -> None: ...

    def subscribe(self, topic: str, qos: int = 0) -> None: ...
    def unsubscribe(self, topic: str) -> None: ...

    def publish(
        self,
        topic: str,
        payload: str | bytes,
        qos: int = 0,
        retain: bool = False,
    ) -> None: ...

    def set_on_message(self, handler: MessageHandler) -> None: ...
    def set_on_connect(self, handler: ConnectHandler) -> None: ...
