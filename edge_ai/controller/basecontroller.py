import multiprocessing as mp
from abc import ABC, abstractmethod


class BaseController(ABC):
    """
    Base class for Sensor Controllers.
    Controllers run sensors in a separate subprocess, and communicate with them
    via pipe.
    """

    def __init__(self):
        self._external_pipe, self._internal_pipe = mp.Pipe(True)
        self._process = mp.Process(
            target=self._internal_loop, args=(self._internal_pipe,), daemon=True
        )

    def start(self):
        self._process.start()

    def stop(self):
        if not self._process.is_alive():
            raise Exception("Attempted to stop controller before starting")

        # close running process
        self._process.kill()

    def read(self):
        self._external_pipe.send(("read",))

        return self._external_pipe.recv()

    @abstractmethod
    def _internal_loop(self, pipe):
        ...
