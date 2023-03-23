from __future__ import annotations

from typing import Type

import Adafruit_ADS1x15

from ..basesensor import BaseSensor
from ...bus import BaseBus, I2C

class ADS1015(BaseSensor):
    CONVERSION_REGISTER = 0x00
    CONFIG_REGISTER = 0x01
    LO_THRESH_REGISTER = 0x02
    HI_THRESH_REGISTER = 0x03

    # Multiplexer (channel comparator values)
    # bits [14:12] on config register
    CH_0_MINUS_1 = 0b000 #default
    CH_0_MINUS_3 = 0b001
    CH_1_MINUS_3 = 0b010
    CH_2_MINUS_3 = 0b011
    CH_0 = 0b100
    CH_1 = 0b101
    CH_2 = 0b110
    CH_3 = 0b111

    # Full Scale Range Values
    # Volt: bit setting
    # bits [11:9] on config register
    RANGES = {
        6.144: 0b000,
        4.096: 0b001,
        2.048: 0b010, #default
        1.024: 0b011,
        0.512: 0b100,
        0.256: 0b101
    }

    # Operating Mode
    # bit 8 on config register
    MODE_CONTINUOUS = 0b0
    MODE_SINGLE = 0b1 # default

    # Data Rate Setting
    # bits 7:5 on config register
    DATARATES = {
        128:  0b000,
        250:  0b001,
        490:  0b010,
        920:  0b011,
        1600: 0b100, # default
        2400: 0b101,
        3300: 0b110
    }

    # Comparator Mode
    # bit 4 on config register
    COMP_TRADITIONAL = 0b0 #default
    COMP_WINDOW = 0b1

    # Comparator Polarity
    # bit 3 on config register
    COMP_POL_LOW = 0b0 # default
    COMP_POL_HIGH = 0b1

    # Latching comparator
    # bit 2 on config register
    LATCH_OFF = 0b0 # default
    LATCH_ON = 0b1

    # Comparator queue
    # Bits [1:0] on config register
    ASSERT_AFTER_1 = 0b00
    ASSERT_AFTER_2 = 0b01
    ASSERT_AFTER_4 = 0b10
    QUEUE_OFF = 0b11 # default

    def __init__(self, bus: Type[BaseBus]) -> None:
        super().__init__(bus)

        # set up the bus
        self._adc = Adafruit_ADS1x15.ADS1015(address = self._address,
                                             busnum = self._busnum)
        # defaults
        self._adc_gain = 1

    @staticmethod
    def I2C(address: int = 0x48, busnum: int = 1) -> ADS1015:
        bus = I2C(address, busnum)
        return ADS1015(bus)

    def start_single(self, channel: int = 0) -> None:
        self._adc.start_adc(channel, gain = self._adc_gain)

    def start_diff(self, differential: int = 0) -> None:
        self._adc.start_adc_difference(differential, gain = self._adc_gain)

    def stop(self) -> None:
        self._adc.stop_adc()

    def read(self) -> float:
        raw_diff = self._adc.get_last_result()
        return self._sensor_raw_value_to_v(raw_diff)

    def read_single(self, channel: int = 0) -> float:
        raw = self._adc.read_adc(channel)
        return self._sensor_raw_value_to_v(raw)

    def read_diff(self, differential: int = 0) -> float:
        raw = self._adc.read_adc_difference(differential)
        return self._sensor_raw_value_to_v(raw)

    # TODO: ADC gain setters
    @staticmethod
    def _sensor_raw_value_to_v(value: int) -> float:
        return value * 4.096 * 2 / 4096
