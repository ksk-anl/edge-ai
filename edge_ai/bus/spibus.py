import spidev

from .basebus import BaseBus

class SPIBus(BaseBus):
    def __init__(self, busnum, cs, maxspeed = 1_000_000, mode = 3):
        self.busnum = busnum
        self.cs = cs
        self.maxspeed = maxspeed
        self.mode = mode
    
    def start(self):
        self.spi = spidev.SpiDev()
        self.spi.max_speed_hz = self.maxspeed
        self.spi.mode = self.mode
        self.spi.open(self.busnum, self.cs)
        
    def read_register(self, address):
        to_read = [address | 0x80, 0x00]
        
        return self.spi.xfer2(to_read)[1]
    
    def write_register(self, address, value):
        to_write = [address, value]
        
        self.spi.xfer2(to_write)
    
    #TODO: Multibyte version?