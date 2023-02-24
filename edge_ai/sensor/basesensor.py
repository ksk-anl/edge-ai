from abc import ABC, abstractmethod

class BaseSensor(ABC):
    def __init__(self) -> None:
        super().__init__()
    
    @property
    @abstractmethod
    def _process(self):
        return self._process
        ...
    
    @abstractmethod
    def start(self):
        ...
    
    @abstractmethod
    def stop(self):
        ...
        
    @abstractmethod
    def read(self):
        ...