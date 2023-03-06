import multiprocessing as mp

from multiprocessing.connection import Connection

from .. import BaseSensor

class LIS3DH(BaseSensor):
    DATARATES = {
        1:    1,
        10:   2,
        25:   3,
        50:   4,
        100:  5,
        200:  6,
        400:  7,
        1600: 8,
        1344: 9,
        5376: 9
        }

    # def __init__(self, bus: Type[BaseBus], debug = False) -> None:
    def __init__(self, debug = False) -> None:
        # super().__init__(bus, debug)
        super().__init__(debug)

        # defaults
        self._lowpower = True
        self._scale = 2
        self._datarate = 5376
        self._selftest = None
        
    @staticmethod
    def SPI(busnum, cs, maxspeed = 1_000_000, mode = 3, debug = False) -> 'LIS3DH':
        sensor = LIS3DH(debug)
        sensor._bustype = 'spi'
        sensor._busconfig = {
            'busnum' : busnum,
            'cs' : cs,
            'maxspeed' : maxspeed,
            'mode' : mode,
            'debug' : debug
        }
        return sensor

    @staticmethod
    def I2C(address, debug = False) -> 'LIS3DH':
        sensor = LIS3DH(debug)
        sensor._bustype = 'i2c'
        sensor._busconfig = {
            'address' : address,
            'debug' : debug
        }
        return sensor

    def _enable_axes(self, x = True, y = True, z = True):
        cfg = self._bus.read_register(0x20)

        if x: 
            cfg |= 0b001
        if y: 
            cfg |= 0b010
        if z:
            cfg |= 0b100
            
        self._bus.write_register(0x20, cfg)

    def _set_datarate(self, datarate):
        #TODO: Make datarate and lowpower settings more robust
        if datarate not in self.DATARATES.keys():
            raise "Data Rate must be one of: 1, 10, 25, 50, 100, 200, 400, 1600, 1344, 5376Hz"

        cfg = self._bus.read_register(0x20)
        
        cfg |= self.DATARATES[datarate] << 4

        self._bus.write_register(0x20, cfg)
        
        if (datarate == 1600) | (datarate == 5376):
            self._set_lowpower(True)

    def _set_lowpower(self, lowpower = False):
        cfg = self._bus.read_register(0x20)
        
        # set LPen bit on register 20 to either on or off
        if lowpower:
            cfg |= 0b00001000
        else:
            cfg &= 0b11110111
        
        self._bus.write_register(0x20, cfg)
        
    def _set_selftest(self, value):
        if value == None: 
            return
        
        cfg = self._bus.read_register(0x23)
        
        cfg &= 0b001
        
        if value == 'high':
            cfg |= 0b100
        elif value == 'low':
            cfg |= 0b010

        self._bus.write_register(0x23, cfg)

    def _enable_highpass(self):
        if not self._highpass:
            return

        cfg = self._bus.read_register(0x21)
        
        cfg |= 0b10001000
        
        self._bus.write_register(0x21, cfg)

    def _setup(self):
        #TODO: setter and config for scale
        self._enable_axes(self.x, self.y, self.z)
        self._set_datarate(self._datarate)
        self._set_selftest(self._selftest)
        self._enable_highpass()

    def _read_sensors_lowpower(self):
        x = self._bus.read_register(0x29)
        y = self._bus.read_register(0x2B)
        z = self._bus.read_register(0x2D)
        
        return (x, y ,z)

    def _new_data_available(self) -> bool:
        status = self._bus.read_register(0x27)
        status = (status >> 3) & 1
        return status

    def _convert_to_gs(self, value) -> float:
        if self._lowpower:
            BITS = 8
            
        max_val = 2**8
        if value > max_val/2.:
            value -= max_val

        return float(value) / ((max_val/2)/self._scale)

    def _internal_loop(self, pipe: Connection):
        # this is a loop that manages the running of the sensor.

        # Initialize Bus
        self._bus = self._initialize_bus(self._bustype, self._busconfig)
        self._bus.start()
        
        # Write any settings, config, etc
        self._setup()
        
        latest_value = None
        while True:
            # if there's new data in the sensor, update latest value
            if self._new_data_available():
                #TODO: non-lowpower version
                raw_values = self._read_sensors_lowpower()
                latest_value = [self._convert_to_gs(value) for value in raw_values]

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

    @property
    def datarate(self):
        return self._datarate
    
    @datarate.setter
    def datarate(self, rate):
        if rate not in self.DATARATES.keys():
            raise "Data Rate must be one of: 1, 10, 25, 50, 100, 200, 400, 1600, 1344, 5376Hz"

        self._datarate = rate

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        
    @property
    def x(self) -> bool:
        return self._x_enabled

    @x.setter
    def x(self, value):
        self._x_enabled = value
        
    @property
    def y(self) -> bool:
        return self._z_enabled

    @y.setter
    def y(self, value):
        self._y_enabled = value
        
    @property
    def z(self) -> bool:
        return self._z_enabled

    @z.setter
    def z(self, value):
        self._z_enabled = value

    def enable_axes(self, x = True, y = True,z = True):
        self.x = x
        self.y = y
        self.z = z
    
    def selftest(self, test = None):
        self._selftest = test
        
    def highpass(self, enable = False):
        self._highpass = enable