import smbus2

import multiprocessing

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

        self.i2c = smbus2.SMBus(busnum)
        
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
    def __init__(self, busnum, address, **kwargs):
        super().__init__(busnum, address, **kwargs)
        self.i2c = smbus2.SMBus(busnum)
        self.address = address
        
    # ----------- Config Functions ---------------
    # TODO: The rest of the config functions
    def set_lowpower(self, lowpower = False):
        cfg = self.read_register(0x20)
        
        # set LPen bit on register 20 to either on or off
        if lowpower:
            cfg |= 0b00001000
        else:
            cfg &= 0b11110111
        
        self.write_register(0x20, cfg)
    
    def enable_axes(self, x = True, y = True, z = True):
        cfg = self.read_register(0x20)

        if x: 
            cfg |= 0b001
        if y: 
            cfg |= 0b010
        if z:
            cfg |= 0b100
        
        self.write_register(0x20, cfg)
    
    def set_datarate(self, datarate):
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
        
        if datarate not in DATARATES.keys():
            raise "Data Rate must be one of: 1, 10, 25, 50, 100, 200, 400, 1600, 1344, 5376Hz"

        cfg = self.read_register(0x20)
        
        cfg |= DATARATES[datarate] << 4
        self.write_register(0x20, cfg)
        
        if (datarate == 1600) | (datarate == 5376):
            self.set_lowpower(True)