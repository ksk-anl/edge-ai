from multiprocessing.connection import Connection

import edge_ai.sensor.accel as accel
from .basecontroller import BaseController

class LIS3DH(BaseController):
    def __init__(self, mode, debug = False) -> None:
        super().__init__()

        self._mode = mode
        self._busconfig = None

        self.DEBUG = debug

    @staticmethod
    def SPI(busnum, cs, maxspeed = 1_000_000, mode = 3, debug = False) -> 'LIS3DH':
        controller = LIS3DH('spi')
        controller._busconfig = {
            'busnum': busnum,
            'cs': cs,
            'maxspeed': maxspeed,
            'mode': mode,
            'debug': debug
        }
        return controller

    @staticmethod
    def I2C(address, busnum, debug = False) -> 'LIS3DH':
        controller = LIS3DH('i2c', debug)
        controller._busconfig = {
            'address': address,
            'busnum': busnum,
            'debug': debug
        }
        return controller

    def _initialize_sensor(self)-> accel.LIS3DH:
        if self._mode == 'spi':
            return accel.LIS3DH.SPI(**self._busconfig)
        elif self._mode == 'i2c':
            return accel.LIS3DH.I2C(**self._busconfig)
            
    # def start(self):
    #     pass
    
    # def stop(self):
    #     pass

    def _internal_loop(self, pipe: Connection):
        # this is a loop that manages the running of the sensor.

        # Initialize Bus
        # self._bus = self._initialize_bus(self._bustype, self._busconfig)
        sensor = self._initialize_sensor()
        sensor.start()
        
        # Write any settings, config, etc
        #TODO: Setup sensor configs from the controller
        # self._setup()
        
        latest_value = None
        while True:
            # if there's new data in the sensor, update latest value
            if sensor._new_data_available():
                #TODO: non-lowpower version
                raw_values = sensor._read_sensors_lowpower()
                latest_value = [sensor._convert_to_gs(value) for value in raw_values]

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