from typing import Any, Type
from abc import ABC, abstractmethod

from ..bus import BaseBus


class BaseSensor(ABC):
    def __init__(self, bus: Type[BaseBus]) -> None:
        self._bus = bus
        self._running = False

        self.start()

    @staticmethod
    def _combine_bytes(high: int, low: int, bits: int) -> int:
        shift = 16 - bits
        high = high << 8 - shift
        low = low >> shift

        return high | low


    def start(self) -> None:
        if self._running:
            return

        self._bus.start()
        self._running = True

    def stop(self) -> None:
        if not self._running:
            raise Exception("Attempted to stop sensor before starting")

        self._bus.stop()
        self._running = False

    @abstractmethod
    def read(self) -> Any:
        ...