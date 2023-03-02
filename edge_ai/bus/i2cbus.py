import smbus2

from .basebus import BaseBus

class I2CBus(BaseBus):
    def __init__(self, address):
        self._address = address
        
    def start(self):
        self.i2c = smbus2.SMBus(self._address)
        
    def write_register(self, address, value):
        self.i2c.write_byte_data(address, value)
        
    def read_register(self, address):
        return self.i2c.read_byte_data(address)