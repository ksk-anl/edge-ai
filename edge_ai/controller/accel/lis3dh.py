from __future__ import annotations

import datetime
import time
from multiprocessing.connection import Connection

import edge_ai.sensor as sensor

from ..basecontroller import BaseController


class LIS3DH(BaseController):
    def __init__(self, interface: str, busconfig: dict[str, int]) -> None:
        super().__init__()

        self._busconfig = busconfig
        self._interface = interface

        # defaults
        self._continuous_mode = True
        self._resolution = "low"
        self._measurement_range = 2
        self._datarate = 5376
        self._selftest = "off"
        self._highpass = False
        self._adc = False
        self._x = True
        self._y = True
        self._z = True

    @staticmethod
    def SPI(busnum: int, cs: int, maxspeed: int = 10_000_000, mode: int = 3) -> LIS3DH:
        busconfig = {"busnum": busnum, "cs": cs, "maxspeed": maxspeed, "mode": mode}
        controller = LIS3DH("spi", busconfig)
        return controller

    @staticmethod
    def I2C(address: int, busnum: int) -> LIS3DH:
        busconfig = {"address": address, "busnum": busnum}
        controller = LIS3DH("i2c", busconfig)
        return controller

    def set_continuous_mode(self, continuous: bool) -> None:
        self._continuous_mode = continuous

    def set_measurement_range(self, measurement_range: int) -> None:
        if measurement_range not in sensor.accel.LIS3DH.MEASUREMENT_RANGES:
            raise Exception(
                f"Measurement range must be one of: {', '.join([str(range) for range in sensor.accel.LIS3DH.MEASUREMENT_RANGES])}"
            )

        self._measurement_range = measurement_range

    def set_datarate(self, datarate: int) -> None:
        if datarate not in sensor.accel.LIS3DH.DATARATES.keys():
            raise Exception(
                f'Data Rate must be one of: {", ".join(sensor.accel.LIS3DH.DATARATES.keys())}'
            )

        self._datarate = datarate

    def set_resolution(self, resolution: str) -> None:
        if resolution not in sensor.accel.LIS3DH.RESOLUTIONS.keys():
            raise Exception(
                f'Resolution must be one of: {", ".join(sensor.accel.LIS3DH.RESOLUTIONS.keys())}'
            )

        self._resolution = resolution

    def set_selftest(self, mode: str = "high") -> None:
        if mode not in sensor.accel.LIS3DH.SELFTEST_MODES:
            raise Exception(
                f"Selftest Mode must be one of: {' ,'.join(sensor.accel.LIS3DH.SELFTEST_MODES)}"
            )

        self._selftest = mode

    def enable_highpass(self, highpass: bool = True) -> None:
        self._highpass = highpass

    def enable_axes(self, x: bool = True, y: bool = True, z: bool = True) -> None:
        self._x = x
        self._y = y
        self._z = z

    def enable_adc(self, adc: bool = True) -> None:
        self._adc = adc
        if adc:
            self._continuous_mode = False

    def read_for(
        self, seconds: float = 0, timeformat: str = "%Y-%m-%d %H:%M:%S.%f"
    ) -> list[tuple[str, list[float]]]:
        self._external_pipe.send(("read for", seconds, timeformat))

        return self._external_pipe.recv()

    def read_adc(self, channel: int) -> float:
        self._external_pipe.send(("read adc", channel))

        return self._external_pipe.recv()

    def _read_for(
        self, seconds: float, timeformat: str
    ) -> list[tuple[str, list[float]]]:
        start = time.time()

        results = []

        while time.time() < start + seconds:
            if self._sensor.new_data_available():
                results.append(
                    (f"{datetime.datetime.now():{timeformat}}", self._sensor.read())
                )

        return results

    def _initialize_sensor(self) -> sensor.accel.LIS3DH:
        if self._interface == "spi":
            return sensor.accel.LIS3DH.SPI(**self._busconfig)
        elif self._interface == "i2c":
            return sensor.accel.LIS3DH.I2C(**self._busconfig)
        else:
            raise Exception("Mode must be spi or i2c")

    def _configure_sensor(self) -> None:
        self._sensor.set_continuous_mode(self._continuous_mode)
        self._sensor.set_resolution(self._resolution)
        self._sensor.set_datarate(self._datarate)
        self._sensor.set_measurement_range(self._measurement_range)
        self._sensor.enable_axes(self._x, self._y, self._z)
        self._sensor.set_selftest(self._selftest)
        self._sensor.enable_highpass(self._highpass)
        self._sensor.enable_adc(self._adc)

    def _internal_loop(self, pipe: Connection) -> None:
        # This is a loop that manages the running of the sensor.
        # This function starts when Controller.start() is called, and
        # runs in a subprocess.

        # Initialize Sensor
        self._sensor = self._initialize_sensor()

        # Write any settings, config, etc
        self._configure_sensor()

        while True:
            # poll the pipe for messages from the parent process
            if pipe.poll():
                message = pipe.recv()

                # if pipe says "read", send out the data into the pipe
                if message[0] == "read":
                    pipe.send(self._sensor.read())
                elif message[0] == "read for":
                    pipe.send(self._read_for(message[1], message[2]))
                elif message[0] == "read adc":
                    pipe.send(self._sensor.read_adc(message[1]))
