
import Adafruit_ADS1x15

import multiprocessing as mp

from multiprocessing.connection import Connection

from . import BaseSensor

class ADS1015(BaseSensor):
    # This currently uses the Adafruit ADS1x15 library.
    # Might be a good idea to generalize this by using spidev/smbus, 
    # but thajt would take time we don't have right now
    
    def __init__(self, address = 0x48, busnum = 1, debug = False) -> None:
        super().__init__(debug)

        self._address = address
        self._busnum = busnum

        # defaults
        self._adc_gain = 1
    
    def _internal_loop(self, pipe: Connection):
        
        # set up the bus
        self._adc = Adafruit_ADS1x15.ADS1015(address = self._address, 
                                             busnum = self._busnum)

        diff = 0
        while True:
            # poll the pipe
            if pipe.poll():
                message = pipe.recv()

                if self.DEBUG:
                    print(f"'{message}' signal received")
                
                # if pipe says "read", send out the data into the pipe
                if message == "read":
                    
                    if self.DEBUG:
                        print(f"Sending latest value '{diff}'...")
                    
                    pipe.send(diff)

            diff = self._adc.read_adc_difference(0, gain = self._adc_gain)

            #TODO: Generalize this
            diff = diff*4.096*2/4096