from abc import ABC, abstractmethod


class BaseBus(ABC):
    def __init__(self):
        ...
        
    @abstractmethod
    def start(self):
        ...
        
    @abstractmethod
    def read_register(self, address):
        ...

    @abstractmethod
    def write_register(self, address, value):
        ...