import multiprocessing as mp

from typing import Type
from abc import ABC, abstractmethod
from multiprocessing.connection import Connection

from ..bus import BaseBus, SPIBus, I2CBus

class BaseSensor(ABC):
    def __init__(self, debug = False) -> None:
        self._external_pipe, self._internal_pipe = mp.Pipe(True)
        self._bustype = None
        self._busconfig = None
        self._running = False
        
        self.DEBUG = debug
    
    def start(self):
        self._running = True
        self._process = mp.Process(target = self._internal_loop, 
                                   args = (self._internal_pipe, ))
        self._process.start()
    
    def stop(self):
        # close running process
        self._running = False
        self._process.kill()
        
    def read(self):
        if self.DEBUG:
            print("Sending 'read' down the pipe...")

        self._external_pipe.send("read")
        
        if self.DEBUG:
            print("Waiting for return from pipe...")
        
        return self._external_pipe.recv()

    @staticmethod
    def _initialize_bus(bustype, busconfig) -> Type[BaseBus]:
        if bustype == 'spi':
            return SPIBus(**busconfig)
        elif bustype == 'i2c':
            return I2CBus(**busconfig)

    @abstractmethod
    def _internal_loop(self, pipe: Connection):
        ...