import spidev
import smbus2

import multiprocessing as mp

from typing import Type
from multiprocessing.connection import Connection

from . import BaseSensor
from ..bus import BaseBus, SPIBus, I2CBus

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

    def __init__(self, bus: Type[BaseBus], debug = False) -> None:
        super().__init__(bus, debug)

        self._lowpower = True
        self._scale = 2
        
    @staticmethod
    def SPI(busnum, cs, maxspeed = 1_000_000, mode = 3, debug = False) -> 'LIS3DH':
        sensor = LIS3DH(debug)
        sensor._busconfig = {
            'type' : 'spi',
            'busnum' : busnum,
            'cs' : cs,
            'maxspeed' : maxspeed,
            'mode' : mode,
            'debug' : debug
        }
        return sensor

    @staticmethod
    def I2C(address, debug = False) -> 'LIS3DH':
        sensor = LIS3DH(debug)
        sensor._busconfig = {
            'type' : 'spi',
            'address' : address,
            'debug' : debug
        }
        return sensor

    def _enable_axes(self, x = True, y = True, z = True):
        cfg = self._bus.read_register(0x20)

        if x: 
            cfg |= 0b001
        if y: 
            cfg |= 0b010
        if z:
            cfg |= 0b100
            
        self._bus.write_register(0x20, cfg)

    def _set_datarate(self, datarate):
        #TODO: Make datarate and lowpower settings more robust
        if datarate not in self.DATARATES.keys():
            raise "Data Rate must be one of: 1, 10, 25, 50, 100, 200, 400, 1600, 1344, 5376Hz"

        cfg = self._bus.read_register(0x20)
        
        cfg |= self.DATARATES[datarate] << 4

        self._bus.write_register(0x20, cfg)
        
        if (datarate == 1600) | (datarate == 5376):
            self._set_lowpower(True)

    def _set_lowpower(self, lowpower = False):
        cfg = self._bus.read_register(0x20)
        
        # set LPen bit on register 20 to either on or off
        if lowpower:
            cfg |= 0b00001000
        else:
            cfg &= 0b11110111
        
        self._bus.write_register(0x20, cfg)

    def _setup(self):
        self._enable_axes(x = True, y = True, z = True)
        self._set_datarate(self._datarate)

    def _read_sensors_lowpower(self):
        x = self._bus.read_register(0x29)
        y = self._bus.read_register(0x2B)
        z = self._bus.read_register(0x2D)
        
        return (x, y ,z)

    def _new_data_available(self) -> bool:
        status = self._bus.read_register(0x27)
        status = (status >> 3) & 1
        return status

    def _internal_loop(self, busconfig: dict, pipe: Connection):
        # this is a loop that manages the running of the sensor.

        # Initialize Bus
        bus = self._initialize_bus(busconfig)
        bus.start()
        
        # Write any settings, config, etc
        self._setup()
        
        latest_value = None
        while True:
            # if there's new data in the sensor, update latest value
            # if self._new_data_available():
            #     #TODO: non-lowpower version
            latest_value = self._read_sensors_lowpower()

            # poll the pipe
            if pipe.poll():
                message = pipe.recv()

                if self.DEBUG:
                    print(f"'{message}' signal received")
                
                # if pipe says "read", send out the data into the pipe
                if message == "read":
                    
                    if self.DEBUG:
                        print(f"Sending latest value '{latest_value}'...")
                    
                    pipe.send(latest_value)

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