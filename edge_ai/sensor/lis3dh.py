import multiprocessing as mp

from typing import Type
from multiprocessing.connection import Connection

from . import BaseSensor
from ..bus import BaseBus

class LIS3DH(BaseSensor):
    def __init__(self, bus: Type[BaseBus]) -> None:
        super().__init__(bus)
    
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