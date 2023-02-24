import multiprocessing as mp

from multiprocessing.connection import Connection

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

    def __internal_loop(self, pipe: Connection):
        # this is a loop that manages the running of the sensor.
        latest_value = None
        
        while True:
            # poll the pipe
            if pipe.poll():
                message = pipe.recv()
            
            # if pipe says "read", send out the data into the pipe

            # if there's new data in the sensor, update latest value
            pass
        pass