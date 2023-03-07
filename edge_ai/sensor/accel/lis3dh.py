import multiprocessing as mp

from typing import Type
from multiprocessing.connection import Connection

from ..basesensor import BaseSensor
from ...bus import BaseBus, I2CBus, SPIBus

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
    # def __init__(self, debug = False) -> None:
        super().__init__(bus, debug)
        # super().__init__(debug)

        # defaults
        self._lowpower = True
        self._scale = 2
        self._datarate = 5376
        self._selftest = None
        self._highpass = False
        
    @staticmethod
    def SPI(busnum, cs, maxspeed = 1_000_000, mode = 3, debug = False) -> 'LIS3DH':
        bus = SPIBus(busnum, cs, maxspeed, mode, debug)
        return LIS3DH(bus, debug)

    @staticmethod
    def I2C(address, busnum, debug = False) -> 'LIS3DH':
        bus = I2CBus(address, busnum, debug)
        return LIS3DH(bus, debug)

    def set_datarate(self, datarate):
        #TODO: Make datarate and lowpower settings more robust
        if datarate not in self.DATARATES.keys():
            raise "Data Rate must be one of: 1, 10, 25, 50, 100, 200, 400, 1600, 1344, 5376Hz"

        cfg = self._bus.read_register(0x20)
        
        cfg |= self.DATARATES[datarate] << 4

        self._bus.write_register(0x20, cfg)
        
        if (datarate == 1600) | (datarate == 5376):
            self.set_lowpower(True)

    def set_lowpower(self, lowpower = False):
        self._lowpower = lowpower
        cfg = self._bus.read_register(0x20)
        
        # set LPen bit on register 20 to either on or off
        if lowpower:
            cfg |= 0b00001000
        else:
            cfg &= 0b11110111
        
        self._bus.write_register(0x20, cfg)
        
    def set_selftest(self, selftest_mode = None):
        cfg = self._bus.read_register(0x23)
        
        cfg &= 0b001
        
        if selftest_mode is None:
            pass
        elif selftest_mode == 'high':
            cfg |= 0b100
        elif selftest_mode == 'low':
            cfg |= 0b010

        self._bus.write_register(0x23, cfg)

    def enable_highpass(self, highpass_on = False):
        cfg = self._bus.read_register(0x21)
        
        if highpass_on:
            cfg |= 0b10001000
        else:
            cfg &= 0b00000111
        
        self._bus.write_register(0x21, cfg)
            
    def enable_axes(self, x = True, y = True, z = True):
        cfg = self._bus.read_register(0x20)

        if x: 
            cfg |= 0b001
        if y: 
            cfg |= 0b010
        if z:
            cfg |= 0b100
            
        self._bus.write_register(0x20, cfg)

    def read(self):
        # TODO: generalize this to other resolutions
        raw_values = self._read_sensors_lowpower()
        return [self._convert_to_gs(value) for value in raw_values]

    def new_data_available(self) -> bool:
        status = self._bus.read_register(0x27)
        status = (status >> 3) & 1
        return status

    def _read_sensors_lowpower(self):
        x = self._bus.read_register(0x29)
        y = self._bus.read_register(0x2B)
        z = self._bus.read_register(0x2D)
        
        return (x, y ,z)

    def _convert_to_gs(self, value) -> float:
        if self._lowpower:
            BITS = 8
            
        max_val = 2**BITS
        if value > max_val/2.:
            value -= max_val

        return float(value) / ((max_val/2)/self._scale)