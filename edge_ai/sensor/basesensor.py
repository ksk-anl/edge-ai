import multiprocessing as mp

from typing import Type
from abc import ABC, abstractmethod

from ..bus import BaseBus


class BaseSensor(ABC):
    def __init__(self, bus: Type[BaseBus], debug = False) -> None:
        self._bus = bus
        self._running = False

        self._external_pipe, self._internal_pipe = mp.Pipe(True)
        self.DEBUG = debug

        self.start()
    
    def start(self):
        if self._running:
            return

        self._bus.start()
        self._running = True
    
    def stop(self):
        if not self._running:
            return

        self._bus.stop()
        self._running = False
        
    @abstractmethod
    def read(self):
        ...