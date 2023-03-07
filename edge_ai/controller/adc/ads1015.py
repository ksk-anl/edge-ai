
from multiprocessing.connection import Connection

import edge_ai.sensor as sensor
from ..basecontroller import BaseController

class ADS1015(BaseController):
    def __init__(self, address = 0x48, busnum = 1, debug = False) -> None:
        super().__init__(debug)
        self._address = address
        self._busnum = busnum

        # set up the bus
        # defaults
        self._adc_gain = 1

        self.DEBUG = debug

    def _initialize_sensor(self)-> sensor.adc.ADS1015:
        return sensor.adc.ADS1015(self._address, self._busnum, self.DEBUG)

    def _internal_loop(self, pipe: Connection):
        # this is a loop that manages the running of the sensor.

        # Initialize Sensor
        # self._bus = self._initialize_bus(self._bustype, self._busconfig)
        _sensor = self._initialize_sensor()
        
        # Write any settings, config, etc
        #TODO: Setup sensor configs from the controller
        
        latest_value = None

        # TODO: add more control over which are read/etc
        while True:
            latest_value = _sensor.read_diff(0)

            # poll the pipe
            if pipe.poll():
                message = pipe.recv()

                if self.DEBUG:
                    print(f"'{message}' signal received")
                
                # if pipe says "read", send out the data into the pipe
                if message == "read":
                    
                    if self.DEBUG:
                        print(f"Sending latest value '{latest_value}'...")
                    
                    pipe.send(latest_value)