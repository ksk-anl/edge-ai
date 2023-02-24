import multiprocessing as mp

from . import BaseSensor
from ..bus import BaseBus

class LIS3DH(BaseSensor):
    def __init__(self, bus) -> None:
        super().__init__()
        
        assert issubclass(bus, BaseBus)
        self.bus = bus
        self.pipe_external, self.pipe_internal = mp.Pipe(True)

    def read(self):
        # send "read" message to the internal process (down the pipe)
        
        # read from the pipe and return
        pass
    
    def start(self):
        # run an internal process that can be controlled via pipe message communication
        pass
    
    def stop(self):
        # close running process
        pass

    def __internal_loop(self, pipe):
        # this is a loop that reads from the internal 
        pass