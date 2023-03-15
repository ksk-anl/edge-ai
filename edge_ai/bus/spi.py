import spidev

from .basebus import BaseBus

class SPI(BaseBus):
    def __init__(self, busnum: int, cs: int, maxspeed: int = 1_000_000, mode: int = 3) -> None:
        self._spi = spidev.SpiDev()
        self._spi.open(busnum, cs)
        self._spi.max_speed_hz = maxspeed
        self._spi.mode = mode

    def stop(self) -> None:
        self._spi.close()

    def read_register(self, register: int) -> int:
        to_read = [register | 0x80, 0x00]

        return self._spi.xfer2(to_read)[1]

    def write_register(self, register: int, value: int) -> None:
        to_write = [register, value]

        self._spi.xfer2(to_write)

    #TODO: Multibyte version?