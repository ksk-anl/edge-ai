from abc import ABC, abstractmethod
from textwrap import wrap

from ..bus import BaseBus


class BaseSensor(ABC):
    def __init__(self, bus):
        self._bus = bus
        self._running = False

        self.start()

    @staticmethod
    def _combine_bytes(high, low, bits):
        shift = 16 - bits
        high = high << 8 - shift
        low = low >> shift

        return high | low

    @staticmethod
    def _divide_into_bytes(num):
        binstring = bin(num)[2:]

        bytestrings = wrap(binstring, 8)

        return [int(x) for x in bytestrings]

    def start(self):
        if self._running:
            return

        self._bus.start()
        self._running = True

    def stop(self):
        if not self._running:
            raise Exception("Attempted to stop sensor before starting")

        self._bus.stop()
        self._running = False

    @abstractmethod
    def read(self):
        ...
