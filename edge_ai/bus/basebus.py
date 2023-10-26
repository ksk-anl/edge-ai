from abc import ABC, abstractmethod

class BaseBus(ABC):
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
    def read_register_list(self, register, length):
        ...

    @abstractmethod
    def write_register(self, register, value):
        ...

    @abstractmethod
    def write_register_list(self, register, value):
        ...
