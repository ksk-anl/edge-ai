from __future__ import __annotations__

from typing import List

from abc import ABC, abstractmethod

class BaseBus(ABC):
    @abstractmethod
    def start(self) -> None:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...

    @abstractmethod
    def read_register(self, register: int) -> int:
        ...

    @abstractmethod
    def read_register_list(self, register: int, length: int) -> List[int]:
        ...

    @abstractmethod
    def write_register(self, register: int, value: int) -> None:
        ...

    @abstractmethod
    def write_register_list(self, register: int, value: List[int]) -> None:
        ...