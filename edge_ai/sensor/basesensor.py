from typing import Any, Type
from abc import ABC, abstractmethod

from ..bus import BaseBus


class BaseSensor(ABC):
    def __init__(self, bus: Type[BaseBus]) -> None:
        self._bus = bus

    def stop(self) -> None:
        self._bus.stop()

    @abstractmethod
    def read(self) -> Any:
        ...