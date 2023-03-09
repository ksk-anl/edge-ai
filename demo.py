import math
import time
import argparse

import edge_ai.controller as controller
import edge_ai.sensor as sensor

def allow_kbinterrupt(f):
    def inner():
        try:
            f()
        except KeyboardInterrupt:
            print("Keyboard Interrupt detected, ending demo...\n")
    return inner

def test_i2c_motion_sensor():
    pass

@allow_kbinterrupt
def test_spi_motion_sensor():
    print("Testing Motion Sensor Values:")
    motionsensor = sensor.accel.LIS3DH.SPI(0, 0)
    motionsensor.start()
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()
    motionsensor.set_selftest(None)


    while True:
        values = motionsensor.read()

        final_value = math.sqrt(sum([x**2 for x in values]))

        print(f'{[f"{val: 1.5f}" for val in values]}: {final_value}')

        time.sleep(0.1)

@allow_kbinterrupt
def test_adc():
    adc = sensor.adc.ADS1015()
    adc.start_diff()

    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        print(f"{adc.read()} V")
        time.sleep(0.1)

@allow_kbinterrupt
def adc_ping_when_above_thresh():
    adc = sensor.adc.ADS1015()
    adc.start()
    THRESH = 2.5

    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        if adc.read() > THRESH:
            print(f"Found data above {THRESH} V!")
        time.sleep(0.1)

@allow_kbinterrupt
def adc_triggers_motionsensor():
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

@allow_kbinterrupt
def test_motionsensor_controller():
    motioncontrol = controller.accel.LIS3DH.SPI(0, 0)
    motioncontrol.start()

    while True:
        values = motioncontrol.read()

        final_value = math.sqrt(sum([x**2 for x in values]))

        print(f'{[f"{val: 1.5f}" for val in values]}: {final_value}')

        time.sleep(0.1)

@allow_kbinterrupt
def test_adc_controller():
    adc_controller = controller.adc.ADS1015.I2C(0x48, 1)
    adc_controller.start()

    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        print(f"{adc_controller.read()} V")
        time.sleep(0.1)


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('mode',
    #                     choices=['1', '2', '3', '4', '5', '6', '7'],
    #                     help= 'Choose a mode/sensor to test: 1: i2c motionsensor, 2: spi motionsensor, 3: ADC (analog sensor), 4: ADC ping when above 2.5')

    # args = parser.parse_args()

    while True:
        print("="*25)
        print("Choose a Demo:")
        print("LIS3DH Tests:")
        print("1: Test Motionsensor (I2C)")
        print("2: Test Motionsensor (SPI)")
        print("ADS1015 Tests:")
        print("3: Test ADC")

        choice = input("Enter choice (q to quit):")
        if choice == 'q':
            break
        elif choice == '1':
            test_i2c_motion_sensor()
        elif choice == '2':
            test_spi_motion_sensor()
        elif choice == '3':
            test_adc()
        # elif args.mode == '4':
        #     adc_ping_when_above_thresh()
        # elif args.mode == '5':
        #     adc_triggers_motionsensor()
        # elif args.mode == '6':
        #     test_motionsensor_controller()
        # elif args.mode == '7':
        #     test_adc_controller()

if __name__ == '__main__':
    main()