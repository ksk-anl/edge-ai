import smbus2

from .basebus import BaseBus

class I2CBus(BaseBus):
    def __init__(self, address, busnum, debug = False):
        self._address = address
        self._busnum = busnum
        
    def start(self):
        self.i2c = smbus2.SMBus(self._busnum)
        
    def write_register(self, register, value):
        self.i2c.write_byte_data(self._address, register, value)
        
    def read_register(self, register):
        return self.i2c.read_byte_data(self._address, register)