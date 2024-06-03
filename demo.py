from __future__ import annotations

import math
import time
from typing import Callable

import edge_ai.controller as controller
import edge_ai.sensor as sensor


def allow_kbinterrupt(f: Callable[[], None]) -> Callable[[], None]:
    def inner():
        try:
            f()
        except KeyboardInterrupt:
            print("Keyboard Interrupt detected, ending demo...\n")

    return inner


def _format_motionsensor_output(values: list[float]) -> str:
    final_value = math.sqrt(sum([x**2 for x in values]))

    return f'{", ".join([f"{val: 1.5f}" for val in values])}: {final_value}'


def _motionsensor_test(sensor: sensor.accel.LIS3DH) -> None:
    sensor.set_resolution("low")
    sensor.set_datarate(100)
    sensor.set_measurement_range(2)
    sensor.set_selftest("off")
    sensor.set_continuous_mode(False)
    sensor.enable_axes()

    print("Outputting Motion Sensor output, Ctrl + C to stop:")
    while True:
        values = sensor.read()

        print(_format_motionsensor_output(values))

        time.sleep(0.1)


def _motionsensor_adc_test(sensor: sensor.accel.LIS3DH) -> None:
    sensor.set_resolution("low")
    sensor.set_datarate(100)
    sensor.set_measurement_range(2)
    sensor.set_selftest("off")
    sensor.set_continuous_mode(False)
    sensor.enable_adc(True)

    # print(f'Temp config: {sensor._bus.read_register(sensor.TEMP_CFG_REG):08b}')
    # print(f'Config register 4: {sensor._bus.read_register(sensor.CTRL_REG4):08b}')

    print("Outputting Motion Sensor ADC output:")
    while True:
        readings = [sensor.read_adc(i) for i in range(1, 4)]
        print(
            f'Channel 1: {readings[0]: 1.5f}, Channel 2: {readings[1]: 1.5f}, Channel 3: {readings[2]: 1.5f}'
        )
        time.sleep(0.1)


@allow_kbinterrupt
def motionsensor_i2c() -> None:
    motionsensor = sensor.accel.LIS3DH.I2C(0x18, 1)
    _motionsensor_test(motionsensor)


@allow_kbinterrupt
def motionsensor_spi() -> None:
    motionsensor = sensor.accel.LIS3DH.SPI(0, 0)
    _motionsensor_test(motionsensor)


@allow_kbinterrupt
def motionsensor_adc_i2c() -> None:
    motionsensor = sensor.accel.LIS3DH.I2C(0x18, 1)
    _motionsensor_adc_test(motionsensor)


@allow_kbinterrupt
def motionsensor_adc_spi() -> None:
    motionsensor = sensor.accel.LIS3DH.SPI(0, 0)
    _motionsensor_adc_test(motionsensor)


@allow_kbinterrupt
def adc_sensor_i2c() -> None:
    adc = sensor.adc.ADS1015.I2C(address=0x48, busnum=1)
    adc.set_differential_mode()
    adc.set_data_range(4.096)
    adc.start_continuous()

    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        print(f"{adc.read()} V")
        time.sleep(0.1)


@allow_kbinterrupt
def motionsensor_controller_spi() -> None:
    motioncontrol = controller.accel.LIS3DH.SPI(0, 0)
    motioncontrol.start()

    while True:
        values = motioncontrol.read()

        print(_format_motionsensor_output(values))

        time.sleep(0.1)


@allow_kbinterrupt
def motionsensor_controller_i2c() -> None:
    motioncontrol = controller.accel.LIS3DH.I2C(0, 0)
    motioncontrol.start()

    while True:
        values = motioncontrol.read()

        print(_format_motionsensor_output(values))

        time.sleep(0.1)


@allow_kbinterrupt
def motionsensor_adc_controller_spi() -> None:
    motioncontrol = controller.accel.LIS3DH.SPI(0, 0)
    motioncontrol.start()

    while True:
        readings = [motioncontrol.read_adc(i) for i in range(1, 4)]

        print(
            f'Channel 1: {readings[0]: 1.5f}, Channel 2: {readings[1]: 1.5f}, Channel 3: {readings[2]: 1.5f}'
        )

        time.sleep(0.1)


@allow_kbinterrupt
def motionsensor_adc_controller_i2c() -> None:
    motioncontrol = controller.accel.LIS3DH.I2C(0, 0)
    motioncontrol.start()

    while True:
        readings = [motioncontrol.read_adc(i) for i in range(1, 4)]

        print(
            f'Channel 1: {readings[0]: 1.5f}, Channel 2: {readings[1]: 1.5f}, Channel 3: {readings[2]: 1.5f}'
        )

        time.sleep(0.1)


@allow_kbinterrupt
def motionsensor_controller_run_for_spi() -> None:
    motioncontrol = controller.accel.LIS3DH.SPI(0, 0)
    motioncontrol.start()

    print("Running for 10 seconds...")

    values = motioncontrol.read_for(10)

    print(f"First 20 results out of {len(values)}:")

    final_results = [[val[0], _format_motionsensor_output(val[1])] for val in values]

    for line in final_results[:20]:
        print(line)

    motioncontrol.stop()


@allow_kbinterrupt
def motionsensor_controller_run_for_i2c() -> None:
    motioncontrol = controller.accel.LIS3DH.I2C(0, 0)
    motioncontrol.start()

    print("Running for 10 seconds...")

    values = motioncontrol.read_for(10)

    print(f"First 20 results out of {len(values)}:")

    final_results = [[val[0], _format_motionsensor_output(val[1])] for val in values]

    for line in final_results[:20]:
        print(line)

    motioncontrol.stop()


@allow_kbinterrupt
def adc_controller_i2c() -> None:
    adc_controller = controller.adc.ADS1015.I2C(0x48, 1)
    adc_controller.set_data_range(4.096)
    adc_controller.start()

    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        print(f"{adc_controller.read()} V")
        time.sleep(0.1)


@allow_kbinterrupt
def adc_triggers_motionsensor_sensor() -> None:
    adc_threshold = 2.5
    record_length = 1

    motionsensor = sensor.accel.LIS3DH.SPI(0, 0)
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()

    adc = sensor.adc.ADS1015.I2C(0x48, 1)
    adc.set_data_range(4.096)

    motionsensor.start()
    adc.start_adc()

    while True:
        print("Waiting for ADC to go high before recording motion...")

        while True:
            time.sleep(0.1)
            val = adc.read()
            if val > adc_threshold:
                break

        finish = time.time() + record_length
        print(f"Detected high ADC!")
        while time.time() < finish:
            print(f"{_format_motionsensor_output(motionsensor.read())}")
            time.sleep(0.1)


@allow_kbinterrupt
def adc_triggers_motionsensor_controller() -> None:
    adc_threshold = 2.5
    record_length = 1

    motionsensor = controller.accel.LIS3DH.SPI(0, 0)
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()

    adc = controller.adc.ADS1015.I2C(0x48, 1)

    motionsensor.start()
    adc.start()

    while True:
        print("Waiting for ADC to go high before recording motion...")

        while True:
            time.sleep(0.1)
            val = adc.read()
            if val > adc_threshold:
                break

        finish = time.time() + record_length
        print(f"Detected high ADC!")
        while time.time() < finish:
            print(f"{_format_motionsensor_output(motionsensor.read())}")
            time.sleep(0.1)


TESTS = {
    1: (motionsensor_i2c, "Test LIS3DH (I2C)"),
    2: (motionsensor_spi, "Test LIS3DH (SPI)"),
    3: (motionsensor_adc_i2c, "Test LIS3DH ADC (I2C)"),
    4: (motionsensor_adc_spi, "Test LIS3DH ADC (I2C)"),
    5: (adc_sensor_i2c, "Test ADS1015 (I2C)"),
    6: (motionsensor_controller_i2c, "Test LIS3DH Controller (I2C)"),
    7: (motionsensor_controller_spi, "Test LIS3DH Controller (SPI)"),
    8: (motionsensor_controller_run_for_i2c, "Run LIS3DH for 10 seconds (I2C)"),
    9: (motionsensor_controller_run_for_spi, "Run LIS3DH for 10 seconds (SPI)"),
    10: (motionsensor_adc_controller_i2c, "Test LIS3DH ADC Controller (I2C)"),
    11: (motionsensor_adc_controller_spi, "Test LIS3DH ADC Controller (SPI)"),
    12: (adc_controller_i2c, "Test ADS1015 Controller (I2C)"),
}

# Other tests:
# adc_triggers_motionsensor_sensor()
# adc_triggers_motionsensor_controller()


def main():
    while True:
        print("=" * 30)
        print("Choose a Demo:")
        for key, test in TESTS.items():
            print(f"    {key}: { test[1] }")

        print("\n")
        choice = input("Enter choice (q to quit): ")
        if choice == "q":
            break
        else:
            TESTS[int(choice)][0]()


if __name__ == "__main__":
    main()
