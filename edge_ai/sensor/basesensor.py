import multiprocessing as mp

from typing import Type
from abc import ABC, abstractmethod
from multiprocessing.connection import Connection

from ..bus import BaseBus

class BaseSensor(ABC):
    def __init__(self, bus: Type[BaseBus]) -> None:
        self.pipe_external, self.pipe_internal = mp.Pipe(True)
        self._bus = bus
    
    @property
    def _internal_pipe(self) -> Connection:
        return self.pipe_internal
        
    @property
    def _external_pipe(self) -> Connection:
        return self.pipe_external

    @property
    def _bus(self) -> Type[BaseBus]:
        return self._bus
        
    @property
    def _process(self) -> mp.Process:
        return self._process
    
    def start(self):
        self._process = mp.Process(target = self.__internal_loop, 
                                   args = (self._bus, self._internal_pipe, ))
        self._process.start()
    
    def stop(self):
        # close running process
        self._process.kill()
        
    def read(self):
        self._external_pipe.send("read")
        
        return self._external_pipe.recv()

    @abstractmethod
    def __internal_loop(self, bus: Type[BaseBus], pipe: Connection):
        ...