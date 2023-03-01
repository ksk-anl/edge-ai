import multiprocessing as mp

from typing import Type
from multiprocessing.connection import Connection

from . import BaseSensor
from ..bus import BaseBus

class LIS3DH(BaseSensor):
    DATARATES = {
        1:    1,
        10:   2,
        25:   3,
        50:   4,
        100:  5,
        200:  6,
        400:  7,
        1600: 8,
        1344: 9,
        5376: 9
        }

    def __init__(self, bus: Type[BaseBus]) -> None:
        super().__init__(bus)

        self._lowpower = True
        self._scale = 2
    
    def _setup(self):
        pass

    def __internal_loop(self, bus: Type[BaseBus], pipe: Connection):
        # this is a loop that manages the running of the sensor.

        # Initialize Bus
        bus.start()
        
        # Write any settings, config, etc
        self._setup()

        # bus.write_register()
        
        
        latest_value = None
        while True:
            # poll the pipe
            if pipe.poll():
                message = pipe.recv()
            
            # if pipe says "read", send out the data into the pipe

            # if there's new data in the sensor, update latest value
            pass
        pass
    
    @property
    def datarate(self):
        return self._datarate
    
    @datarate.setter
    def datarate(self, rate):
        if rate not in self.DATARATES.keys():
            raise "Data Rate must be one of: 1, 10, 25, 50, 100, 200, 400, 1600, 1344, 5376Hz"

        self._datarate = rate

    @property
    def scale(self):
        return self._scale