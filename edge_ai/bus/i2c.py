import smbus2

from .basebus import BaseBus

class I2C(BaseBus):
    def __init__(self, address: int, busnum: int) -> None:
        self._address = address

        self._i2c = smbus2.SMBus(busnum)

    def stop(self) -> None:
        self._i2c.close()

    def write_register(self, register: int, value: int) -> None:
        self._i2c.write_byte_data(self._address, register, value)

    def read_register(self, register: int) -> int:
        return self._i2c.read_byte_data(self._address, register)