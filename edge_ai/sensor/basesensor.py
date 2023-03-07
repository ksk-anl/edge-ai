import multiprocessing as mp

from typing import Type
from abc import ABC, abstractmethod
from multiprocessing.connection import Connection

from ..bus import BaseBus


class BaseSensor(ABC):
    def check_if_running(f):
        def inner(self, *args, **kwargs):
            if not self._running:
                raise Exception(f"The sensor ({self.__class__.__name__}) has not been started.")
            f(*args, **kwargs)
        return inner
    
    def __init__(self, bus: Type[BaseBus], debug = False) -> None:
        self._bus = bus
        self._running = False
        
        self._external_pipe, self._internal_pipe = mp.Pipe(True)
        self.DEBUG = debug
    
    def start(self):
        self._bus.start()
        self._running = True
    
    def stop(self):
        self._bus.stop()
        self._running = False
        
    @abstractmethod
    def read(self):
        ...

    # @abstractmethod
    # def _internal_loop(self, pipe: Connection):
    #     ...