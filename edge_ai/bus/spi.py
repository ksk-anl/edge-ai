from __future__ import annotations

import spidev

from .basebus import BaseBus


class SPI(BaseBus):
    def __init__(
        self, busnum, cs, maxspeed = 1_000_000, mode = 3):
        self._busnum = busnum
        self._cs = cs
        self._maxspeed = maxspeed
        self._mode = mode

        self._spi = None

    def _get_bus(self):
        if self._spi is None:
            self.start()

        return self._spi

    def start(self):
        self._spi = spidev.SpiDev()
        self._spi.open(self._busnum, self._cs)
        self._spi.max_speed_hz = self._maxspeed
        self._spi.mode = self._mode

    def stop(self):
        if self._spi is None:
            raise Exception("Attempted to stop bus before starting")

        self._spi.close()

    def write_register(self, register, value):
        to_write = [register, value]

        self._get_bus().xfer2(to_write)

    def write_register_list(self, register, value):
        to_write = [register | 0x80] + value

        return self._get_bus().xfer2(to_write)

    def read_register(self, register):
        to_read = [register | 0x80, 0x00]

        return self._get_bus().xfer2(to_read)[1]

    def read_register_list(self, register, length):
        to_read = [register | 0x80] + [0x00] * length

        return self._get_bus().xfer2(to_read)
