from abc import ABC, abstractmethod

class BaseBus(ABC):
    def __init__(self):
        ...
        
    @abstractmethod
    def start(self):
        ...
        
    @abstractmethod
    def stop(self):
        ...
        
    @abstractmethod
    def read_register(self, register):
        ...

    @abstractmethod
    def write_register(self, register, value):
        ...