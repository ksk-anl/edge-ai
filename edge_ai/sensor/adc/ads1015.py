import Adafruit_ADS1x15

import multiprocessing as mp

from multiprocessing.connection import Connection

from ..basesensor import BaseSensor

class ADS1015(BaseSensor):
    # This currently uses the Adafruit ADS1x15 library.
    # Might be a good idea to generalize this by using spidev/smbus, 
    # but thajt would take time we don't have right now
    
    def __init__(self, address = 0x48, busnum = 1, debug = False) -> None:
        self._address = address
        self._busnum = busnum

        # set up the bus
        self._adc = Adafruit_ADS1x15.ADS1015(address = self._address, 
                                             busnum = self._busnum)
        # defaults
        self._adc_gain = 1
    
    # Overload Base class start implementation
    def start(self):
        self.start_single(0)

    def start_single(self, channel = 0):
        self._adc.start_adc(channel, gain = self._adc_gain)
    
    def start_diff(self, differential = 0):
        self._adc.start_adc_difference(differential, gain = self._adc_gain)

    def stop(self):
        self._adc.stop_adc()

    def read(self):
        raw_diff = self._adc.get_last_result()
        return self._convert_to_v(raw_diff)
    
    def read_single(self, channel = 0):
        raw = self._adc.read_adc(channel)
        return self._convert_to_v(raw)

    def read_diff(self, differential = 0):
        raw = self._adc.read_adc_difference(differential)
        return self._convert_to_v(raw)

    # TODO: ADC gain setters

    @staticmethod
    def _convert_to_v(value) -> float:
        return value * 4.096 * 2 / 4096
    