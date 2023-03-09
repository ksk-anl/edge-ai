from __future__ import annotations

import math
import time

import edge_ai.controller as controller
import edge_ai.sensor as sensor

def allow_kbinterrupt(f):
    def inner():
        try:
            f()
        except KeyboardInterrupt:
            print("Keyboard Interrupt detected, ending demo...\n")
    return inner

def _format_motionsensor_output(values: list[float]) -> str:
    final_value = math.sqrt(sum([x**2 for x in values]))

    return f'{", ".join([f"{val: 1.5f}" for val in values])}: {final_value}'

@allow_kbinterrupt
def motionsensor_i2c() -> None:
    print("Testing Motion Sensor Values:")
    motionsensor = sensor.accel.LIS3DH.I2C(0x18, 1)
    motionsensor.start()
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()
    motionsensor.set_selftest('off')

    while True:
        values = motionsensor.read()

        print(_format_motionsensor_output(values))

        time.sleep(0.1)

@allow_kbinterrupt
def motionsensor_spi() -> None:
    print("Testing Motion Sensor Values:")
    motionsensor = sensor.accel.LIS3DH.SPI(0, 0)
    motionsensor.start()
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()
    motionsensor.set_selftest('off')

    while True:
        values = motionsensor.read()

        print(_format_motionsensor_output(values))

        time.sleep(0.1)

@allow_kbinterrupt
def adc_sensor_i2c() -> None:
    adc = sensor.adc.ADS1015(address = 0x48, busnum = 1)
    adc.start_diff()

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

        final_value = math.sqrt(sum([x**2 for x in values]))

        print(f'{", ".join([f"{val: 1.5f}" for val in values])}: {final_value}')

        time.sleep(0.1)

@allow_kbinterrupt
def adc_controller_i2c() -> None:
    adc_controller = controller.adc.ADS1015.I2C(0x48, 1)
    adc_controller.start()

    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        print(f"{adc_controller.read()} V")
        time.sleep(0.1)

@allow_kbinterrupt
def adc_ping_when_above_thresh() -> None:
    adc = sensor.adc.ADS1015()
    adc.start()
    THRESH = 2.5

    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        if adc.read() > THRESH:
            print(f"Found data above {THRESH} V!")
        time.sleep(0.1)

@allow_kbinterrupt
def adc_triggers_motionsensor() -> None:
    motionsensor = controller.accel.LIS3DH.SPI(0, 0)
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()

    adc = controller.adc.ADS1015()

    motionsensor.start()
    adc.start()
    THRESH = 2.5

    while True:
        print("Waiting for ADC to go high before recording motion...")

        if adc.read() > THRESH:
            print(f'Detected high ADC! motionsensor reading: {motionsensor.read()}')

        time.sleep(0.1)

def main():
    while True:
        print("="*30)
        print("Choose a Demo:")
        print("Sensor Class Tests:")
        print("    LIS3DH Tests:")
        print("    1: Test Motionsensor (I2C)")
        print("    2: Test Motionsensor (SPI)")
        print("    ADS1015 Tests:")
        print("    3: Test ADC")
        print("Controller Class Tests")
        print("    LIS3DH Tests:")
        print("    4: Test Motionsensor (I2C)")
        print("    5: Test Motionsensor (SPI)")
        print("    ADS1015 Tests:")
        print("    6: Test ADC")

        print("\n")
        choice = input("Enter choice (q to quit): ")
        if choice == 'q':
            break
        elif choice == '1':
            motionsensor_i2c()
        elif choice == '2':
            motionsensor_spi()
        elif choice == '3':
            adc_sensor_i2c()
        # elif args.mode == '4':
        #     adc_ping_when_above_thresh()
        elif choice == '5':
            motionsensor_controller_spi()
        elif choice == '6':
            adc_controller_i2c()

if __name__ == '__main__':
    main()