from abc import ABC, abstractmethod

class Sensor(ABC):
    def __init__(self) -> None:
        super().__init__()
        
    @abstractmethod
    def start(self):
        ...
    
    @abstractmethod
    def stop(self):
        ...
        
    @abstractmethod
    def read(self):
        ...