from __future__ import annotations

from multiprocessing.connection import Connection

import edge_ai.sensor as sensor
from ..basecontroller import BaseController

class ADS1015(BaseController):
    def __init__(self, mode, busconfig) -> None:
        super().__init__()
        self._mode = mode
        self._busconfig = busconfig

        # set up the bus
        # defaults
        self._adc_gain = 1

    @staticmethod
    def I2C(address, busnum) -> ADS1015:
        busconfig = {
            'address': address,
            'busnum': busnum
        }
        controller = ADS1015('i2c', busconfig)
        return controller

    def _initialize_sensor(self)-> sensor.adc.ADS1015:
        return sensor.adc.ADS1015(**self._busconfig)

    def _internal_loop(self, pipe: Connection):
        # this is a loop that manages the running of the sensor.

        # Initialize Sensor
        _sensor = self._initialize_sensor()

        # Write any settings, config, etc
        #TODO: Setup sensor configs from the controller

        latest_value = None

        # TODO: add more control over which are read/etc
        while True:
            latest_value = _sensor.read_diff(0)

            # poll the pipe
            if pipe.poll():
                message = pipe.recv()

                # if pipe says "read", send out the data into the pipe
                if message == "read":

                    pipe.send(latest_value)