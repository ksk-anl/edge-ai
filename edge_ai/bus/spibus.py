import spidev

from .basebus import BaseBus

class SPIBus(BaseBus):
    def __init__(self, busnum, cs, maxspeed = 1_000_000, mode = 3, debug = False):
        self.busnum = busnum
        self.cs = cs
        self.maxspeed = maxspeed
        self.mode = mode
    
    def start(self):
        self.spi = spidev.SpiDev()
        self.spi.open(self.busnum, self.cs)
        self.spi.max_speed_hz = self.maxspeed
        self.spi.mode = self.mode

    def stop(self):
        self.spi.close()
        
    def read_register(self, register):
        to_read = [register | 0x80, 0x00]
        
        return self.spi.xfer2(to_read)[1]
    
    def write_register(self, register, value):
        to_write = [register, value]
        
        self.spi.xfer2(to_write)
    
    #TODO: Multibyte version?