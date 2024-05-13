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
    sensor.set_datarate(5376)
    sensor.set_selftest("off")
    sensor.enable_axes()

    print("Outputting Motion Sensor output, Ctrl + C to stop:")
    while True:
        values = sensor.read()

        print(_format_motionsensor_output(values))

        time.sleep(0.1)


def _motionsensor_adc_test(sensor: sensor.accel.LIS3DH) -> None:
    sensor.set_resolution("high")
    sensor.enable_adc()

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


def main():
    while True:
        print("=" * 30)
        print("Choose a Demo:")
        print("Sensor Class Tests:")
        print("    LIS3DH Tests:")
        print("    1: Test Motionsensor (I2C)")
        print("    2: Test Motionsensor (SPI)")
        print("    3: Test Motionsensor ADC (I2C)")
        print("    4: Test Motionsensor ADC (SPI)")
        print("    ADS1015 Tests:")
        print("    5: Test ADC")
        print("    Combined Tests:")
        print("    6: ADC HIGH triggers motion sensor")
        print("Controller Class Tests")
        print("    LIS3DH Tests:")
        print("    7: Test Motionsensor (I2C)")
        print("    8: Test Motionsensor (SPI)")
        print("    9: Test Motionsensor for 10 seconds (I2C)")
        print("    10: Test Motionsensor for 10 seconds (SPI)")
        print("    11: Test Motionsensor ADC (I2C)")
        print("    12: Test Motionsensor ADC (SPI)")
        print("    ADS1015 Tests:")
        print("    13: Test ADC")
        print("Combined Tests:")
        print("    14: ADC HIGH triggers motion sensor")

        print("\n")
        choice = input("Enter choice (q to quit): ")
        if choice == "q":
            break
        elif choice == "1":
            motionsensor_i2c()
        elif choice == "2":
            motionsensor_spi()
        elif choice == "3":
            motionsensor_adc_i2c()
        elif choice == "4":
            motionsensor_adc_spi()
        elif choice == "5":
            adc_sensor_i2c()
        elif choice == "6":
            adc_triggers_motionsensor_sensor()
        elif choice == "7":
            motionsensor_controller_i2c()
        elif choice == "8":
            motionsensor_controller_spi()
        elif choice == "9":
            motionsensor_controller_run_for_i2c()
        elif choice == "10":
            motionsensor_controller_run_for_spi()
        elif choice == "11":
            motionsensor_adc_controller_i2c()
        elif choice == "12":
            motionsensor_adc_controller_spi()
        elif choice == "13":
            adc_controller_i2c()
        elif choice == "14":
            adc_triggers_motionsensor_controller()


if __name__ == "__main__":
    main()
