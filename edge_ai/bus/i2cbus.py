import smbus2

from .basebus import BaseBus

class I2C(BaseBus):
    def __init__(self, address, busnum):
        self._address = address
        self._busnum = busnum

        self._i2c = None
    
    def _get_bus(self):
        if self._i2c is None:
            self.start()
            
        return self._i2c
        
    def start(self):
        self._i2c = smbus2.SMBus(self._busnum)

    def stop(self):
        self._get_bus().close()
        
    def write_register(self, register, value):
        self._get_bus().write_byte_data(self._address, register, value)
        
    def read_register(self, register):
        return self._get_bus().read_byte_data(self._address, register)