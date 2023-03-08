from __future__ import annotations

from multiprocessing.connection import Connection

import edge_ai.sensor as sensor
from ..basecontroller import BaseController

class LIS3DH(BaseController):
    def __init__(self, mode: str, busconfig: dict[str, int]) -> None:
        super().__init__()

        self._busconfig = busconfig
        self._mode = mode

    @staticmethod
    def SPI(busnum: int, cs: int, maxspeed: int = 1_000_000, mode: int = 3) -> LIS3DH:
        busconfig = {
            'busnum': busnum,
            'cs': cs,
            'maxspeed': maxspeed,
            'mode': mode
        }
        controller = LIS3DH('spi', busconfig)
        return controller

    @staticmethod
    def I2C(address: int, busnum: int) -> LIS3DH:
        busconfig = {
            'address': address,
            'busnum': busnum
        }
        controller = LIS3DH('i2c', busconfig)
        return controller

    def _initialize_sensor(self) -> sensor.accel.LIS3DH:
        if self._mode == 'spi':
            return sensor.accel.LIS3DH.SPI(**self._busconfig)
        elif self._mode == 'i2c':
            return sensor.accel.LIS3DH.I2C(**self._busconfig)
        else:
            raise Exception("Mode must be spi or i2c")

    def _internal_loop(self, pipe: Connection) -> None:
        # this is a loop that manages the running of the sensor.

        # Initialize Sensor
        motionsensor = self._initialize_sensor()

        # Write any settings, config, etc
        #TODO: Setup sensor configs from the controller
        motionsensor.set_datarate(5376)
        motionsensor.enable_axes()
        motionsensor.set_selftest('off')

        latest_value = None
        while True:
            # if there's new data in the sensor, update latest value
            if motionsensor.new_data_available():
                latest_value = motionsensor.read()

            # poll the pipe
            if pipe.poll():
                message = pipe.recv()

                # if pipe says "read", send out the data into the pipe
                if message == "read":
                    pipe.send(latest_value)