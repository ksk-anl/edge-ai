from __future__ import annotations

from typing import Type

from ..basesensor import BaseSensor
from ...bus import BaseBus, I2C, SPI

class LIS3DH(BaseSensor):
    DATARATES = {
        1:    1,
        10:   2,
        25:   3,
        50:   4,
        100:  5,
        200:  6,
        400:  7,
        1344: 9,
        1620: 8,
        5376: 9
        }

    def __init__(self, bus: Type[BaseBus]) -> None:
        super().__init__(bus)

        # defaults
        self._resolution = 'low'
        self._scale = 2
        self._datarate = 5376
        self._selftest = None
        self._highpass = False
        
    @staticmethod
    def SPI(busnum, cs, maxspeed = 1_000_000, mode = 3) -> LIS3DH:
        bus = SPI(busnum, cs, maxspeed, mode)
        return LIS3DH(bus)

    @staticmethod
    def I2C(address, busnum) -> LIS3DH:
        bus = I2C(address, busnum)
        return LIS3DH(bus)

    def set_scale(self, scale):
        valid_scales = [2, 4, 8, 16]

        if scale not in valid_scales:
            raise Exception(f"Scale must be one of: {', '.join([str(scale) for scale in valid_scales])}")

    def set_datarate(self, datarate):
        if datarate not in self.DATARATES.keys():
            valid_rates = [str(rate) for rate in self.DATARATES.keys()]
            raise Exception(f"Data Rate must be one of: {', '.join(valid_rates)}Hz")

        if (datarate == 1620) | (datarate == 5376):
            if self._resolution != 'low':
                raise Exception("1620Hz and 5376Hz mode only allowed on Low Power mode")
        
        if datarate == 1344 & self._resolution == 'low':
            raise Exception("1344Hz mode not allowed on Low Power mode")

        cfg = self._bus.read_register(0x20)
        
        cfg |= self.DATARATES[datarate] << 4

        self._bus.write_register(0x20, cfg)
        

    def set_resolution(self, resolution):
        valid_resolutions = ['low', 'normal', 'high']
        if resolution not in valid_resolutions:
            raise Exception(f'Mode must be one of {", ".join(valid_resolutions)}')

        self._resolution = resolution

        if resolution == 'low':
            LPen_bit = True
            HR_bit = False
        elif resolution == 'high':
            LPen_bit = False
            HR_bit = True
        else:
            LPen_bit = False
            HR_bit = False

        cfg = self._bus.read_register(0x20)
        
        if LPen_bit:
            cfg |= 0b00001000 # set LPen bit on register 20 to on
        else:
            cfg &= 0b11110111 # set LPen bit on register 20 to off
    
        self._bus.write_register(0x20, cfg)

        cfg = self._bus.read_register(0x23)
        
        if HR_bit:
            cfg |= 0b00000100 # set HR bit on register 23 to on
        else:
            cfg &= 0b11111011 # set HR bit on register 23 to off
    
        self._bus.write_register(0x23, cfg)
        
    def set_selftest(self, selftest = None):
        cfg = self._bus.read_register(0x23)
        
        cfg &= 0b001
        
        if selftest is None:
            pass
        elif selftest == 'high':
            cfg |= 0b100
        elif selftest == 'low':
            cfg |= 0b010

        self._bus.write_register(0x23, cfg)

    def enable_highpass(self, highpass = True):
        cfg = self._bus.read_register(0x21)
        
        if highpass:
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
        raw_values = self._read_sensors()
        return [self._convert_to_gs(value) for value in raw_values]

    def new_data_available(self) -> bool:
        status = self._bus.read_register(0x27)
        status = (status >> 3) & 1
        return status

    def _read_sensors(self):
        x = self._bus.read_register(0x29)
        y = self._bus.read_register(0x2B)
        z = self._bus.read_register(0x2D)

        if self._resolution != 'low':
            xl = self._bus.read_register(0x28)
            yl = self._bus.read_register(0x2A)
            zl = self._bus.read_register(0x2C)

            if self._resolution == 'high':
                x = (x << 8 | xl) >> 4
                y = (y << 8 | yl) >> 4
                z = (z << 8 | zl) >> 4
            elif self._resolution == 'normal':
                x = (x << 8 | xl) >> 6
                y = (y << 8 | yl) >> 6
                z = (z << 8 | zl) >> 6
        
        return (x, y ,z)

    def _convert_to_gs(self, value) -> float:
        if self._resolution == 'low':
            bits = 8
        elif self._resolution == 'normal':
            bits = 10
        elif self._resolution == 'high':
            bits = 12
            
        max_val = 2**bits
        if value > max_val / 2.:
            value -= max_val

        return float(value) / ((max_val / 2 ) / self._scale)