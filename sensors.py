import smbus2
import math
import time
import datetime
import spidev

import multiprocessing as mp

TIMEFORMAT = '%H:%M:%S.%f'

class Sensor():
    """
    Base class for sensors
    """

    def __init__(self, run_in_subprocess = True):
        self.run_in_subprocess = run_in_subprocess
    
    def run(self):
        return NotImplementedError
    
class I2CSensor(Sensor):
    """
    Class for sensors using the I2C bus
    """
    
    def __init__(self, busnum, address, **kwargs):
        super().__init__(**kwargs)
        self.busnum = busnum
        self.address = address
        
    def write_register(self, register, value):
        """
        Writes a byte value for a specific register of this sensor
        """
        self.i2c.write_byte_data(self.address, register, value)

    def write_registers(self, targets: dict):
        """
        Writes byte values for multiple registers
        Input:
            dict of the form {register: value}
        """
        for (reg, val) in targets.items():
            self.write_register(reg, val)

    def write_i2c_block(self, register, data):
        self.i2c.write_block_data(self.address, register, data)
            
    def read_register(self, register):
        return self.i2c.read_byte_data(self.address, register)

    def read_registers(self, registers):
        return [self.read_register(reg) for reg in registers]
    
    def read_i2c_block(self, register):
        return self.i2c.read_block_data(self.address, register)

    def run(self):
        return NotImplementedError
    
class LIS3DH_I2C(I2CSensor):
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
    
    def __init__(self, busnum, address, **kwargs):
        super().__init__(busnum, address, **kwargs)
        
        # defaults:
        self.low_power_mode = True
        self.x_axis = True
        self.y_axis = True
        self.z_axis = True
        self.datarate = 5376

        # TODO: setter functions for these
        self.high_resolution = False 
        self.scale = 2
        
        
    # ----------- Internal Config Functions ---------------
    # TODO: The rest of the config functions
    def _set_lowpower(self, lowpower = False):
        cfg = self.read_register(0x20)
        
        # set LPen bit on register 20 to either on or off
        if lowpower:
            cfg |= 0b00001000
        else:
            cfg &= 0b11110111
        
        self.write_register(0x20, cfg)
    
    def _enable_axes(self, x = True, y = True, z = True):
        cfg = self.read_register(0x20)

        if x: 
            cfg |= 0b001
        if y: 
            cfg |= 0b010
        if z:
            cfg |= 0b100
        
        self.write_register(0x20, cfg)
    
    def _set_datarate(self, datarate):
        if datarate not in self.DATARATES.keys():
            raise "Data Rate must be one of: 1, 10, 25, 50, 100, 200, 400, 1600, 1344, 5376Hz"

        cfg = self.read_register(0x20)
        
        cfg |= self.DATARATES[datarate] << 4
        self.write_register(0x20, cfg)
        
        if (datarate == 1600) | (datarate == 5376):
            self._set_lowpower(True)
            
    def _setup(self):
        self._set_lowpower(self.low_power_mode)
        self._enable_axes(self.x_axis, self.y_axis, self.z_axis)
        self._set_datarate(self.datarate)

    # ----------------- Data Reading Functions -------
    # TODO: add normal/high resolution versions
    def _read_sensors_lowpower(self):
        x = self.read_register(0x29)
        y = self.read_register(0x2B)
        z = self.read_register(0x2D)
        
        return (x, y ,z)
    
    def _calc_n_lowpower(self, x, y, z):
        max_val = 2**8
        
        if x > max_val/2.:
            x -= max_val
        if y > max_val/2.:
            y -= max_val
        if z > max_val/2.:
            z -= max_val
        
        x = float(x) / ((max_val/2)/self.scale)
        y = float(y) / ((max_val/2)/self.scale)
        z = float(z) / ((max_val/2)/self.scale)

        n = math.sqrt(x**2 + y**2 + z**2)
        return n
    
    # ----------------- Run Functions -------------
    def _run(self, delta_t, output):
        """
        This is the internal function to be run inside the subprocess.
        Records as much data as possible in a given amount of time.
        """
        # attach a new instance of the SMBus object
        self.i2c = smbus2.SMBus(self.busnum)
        
        self._setup()
        
        results = []
        time_end = time.time() + delta_t
        while time.time() <= time_end:
            if self.low_power_mode:
                readings = self._read_sensors_lowpower()
                res = self._calc_n_lowpower(*readings)
                results.append([f'{datetime.datetime.now():{TIMEFORMAT}}', res])
            
        output.put(results)
        self.i2c.close()
    
    def run_for(self, time):
        results = mp.Queue()
        p = mp.Process(target= self._run, args=(time, results))
        p.start()
        output = results.get()
        p.join()
        return output

        
class SPISensor(Sensor):
    def __init__(self, busnum, cs, max_speed = 1000000, mode = 3, run_in_subprocess=True):
        super().__init__(run_in_subprocess)
        self.busnum = busnum
        self.cs = cs
        self.max_speed = max_speed
        self.mode = mode
        
    def write_register(self, address, value):
        to_write = [0x00, 0x00]
        to_write[0] = address
        to_write[1] = value
        
        self.spi.xfer2(to_write)
        
    def read_register(self, address):
        to_read = [0x00, 0x00]
        
        to_read[0] = address
        
        return self.spi.xfer2(to_read)[1]
        
class LIS3DH_SPI(SPISensor):
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
    
    def __init__(self, busnum, cs, max_speed=1000000, mode=3, run_in_subprocess=True):
        super().__init__(busnum, cs, max_speed, mode, run_in_subprocess)

        # defaults:
        self.low_power_mode = True
        self.x_axis = True
        self.y_axis = True
        self.z_axis = True
        self.datarate = 5376

        # TODO: setter functions for these
        self.high_resolution = False 
        self.scale = 2
    
    # ----------- Internal Config Functions ---------------
    # TODO: The rest of the config functions
    def _set_lowpower(self, lowpower = False):
        cfg = self.read_register(0x20)
        
        # set LPen bit on register 20 to either on or off
        if lowpower:
            cfg |= 0b00001000
        else:
            cfg &= 0b11110111
        
        self.write_register(0x20, cfg)
    
    def _enable_axes(self, x = True, y = True, z = True):
        cfg = self.read_register(0x20)

        if x: 
            cfg |= 0b001
        if y: 
            cfg |= 0b010
        if z:
            cfg |= 0b100
        
        self.write_register(0x20, cfg)
    
    def _set_datarate(self, datarate):
        if datarate not in self.DATARATES.keys():
            raise "Data Rate must be one of: 1, 10, 25, 50, 100, 200, 400, 1600, 1344, 5376Hz"

        cfg = self.read_register(0x20)
        
        cfg |= self.DATARATES[datarate] << 4
        self.write_register(0x20, cfg)
        
        if (datarate == 1600) | (datarate == 5376):
            self._set_lowpower(True)

    def _setup(self):
        self._set_lowpower(self.low_power_mode)
        self._enable_axes(self.x_axis, self.y_axis, self.z_axis)
        self._set_datarate(self.datarate)

    # ----------------- Data Reading Functions -------
    # TODO: add normal/high resolution versions
    def _read_sensors_lowpower(self):
        x = self.read_register(0x29 | 0x80 | 0x40)
        y = self.read_register(0x2B | 0x80 | 0x40)
        z = self.read_register(0x2D | 0x80 | 0x40)
        
        return (x, y ,z)
    
    def _calc_n_lowpower(self, x, y, z):
        max_val = 2**8
        
        if x > max_val/2.:
            x -= max_val
        if y > max_val/2.:
            y -= max_val
        if z > max_val/2.:
            z -= max_val
        
        x = float(x) / ((max_val/2)/self.scale)
        y = float(y) / ((max_val/2)/self.scale)
        z = float(z) / ((max_val/2)/self.scale)

        n = math.sqrt(x**2 + y**2 + z**2)
        return n

    def _run(self, delta_t, output):
        """
        This is the internal function to be run inside the subprocess.
        Records as much data as possible in a given amount of time.
        """
        # attach a new instance of the SMBus object
        self.spi = spidev.SpiDev()
        self.spi.open(self.busnum, self.cs)
        self.spi.max_speed_hz = self.max_speed
        self.spi.mode = self.mode
        
        self._setup()
        
        results = []
        time_end = time.time() + delta_t
        while time.time() <= time_end:
            if self.low_power_mode:
                readings = self._read_sensors_lowpower()
                res = self._calc_n_lowpower(*readings)
                results.append([f'{datetime.datetime.now():{TIMEFORMAT}}', res])
            
        output.put(results)
        self.spi.close()

    def run_for(self, time):
        results = mp.Queue()
        p = mp.Process(target= self._run, args=(time, results))
        p.start()
        output = results.get()
        p.join()
        return output