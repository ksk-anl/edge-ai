import multiprocessing as mp

from abc import ABC, abstractmethod
from typing import Type
from multiprocessing.connection import Connection

from ..sensor import BaseSensor

class BaseController(ABC):
    """
    Base class for Sensor Controllers.
    Controllers run sensors in a separate subprocess, and communicate with them
    via pipe.
    """
    def __init__(self, debug = False) -> None:
        self._external_pipe, self._internal_pipe = mp.Pipe(True)

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

    @abstractmethod
    def _internal_loop(self, pipe: Connection):
        ...