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


def _format_motionsensor_output(values):
    final_value = math.sqrt(sum([x**2 for x in values]))

    return '{}: {}'.format(
        ", ".join(["{:1.5f}".format(val) for val in values]), final_value
    )


def _motionsensor_test(sensor):
    sensor.set_resolution("low")
    sensor.set_datarate(5376)
    sensor.set_selftest("off")
    sensor.enable_axes()

    print("Outputting Motion Sensor output, Ctrl + C to stop:")
    while True:
        values = sensor.read()

        print(_format_motionsensor_output(values))

        time.sleep(0.1)


@allow_kbinterrupt
def motionsensor_i2c():
    motionsensor = sensor.accel.LIS3DH.I2C(0x18, 1)
    _motionsensor_test(motionsensor)


@allow_kbinterrupt
def motionsensor_spi():
    motionsensor = sensor.accel.LIS3DH.SPI(0, 0)
    _motionsensor_test(motionsensor)


@allow_kbinterrupt
def adc_sensor_i2c():
    adc = sensor.adc.ADS1015.I2C(address=0x48, busnum=1)
    adc.set_differential_mode()
    adc.set_data_range(4.096)
    adc.start_continuous()

    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        print("{} V".format(adc.read()))
        time.sleep(0.1)


@allow_kbinterrupt
def motionsensor_controller_spi():
    motioncontrol = controller.accel.LIS3DH.SPI(0, 0)
    motioncontrol.start()

    while True:
        values = motioncontrol.read()

        print(_format_motionsensor_output(values))

        time.sleep(0.1)


@allow_kbinterrupt
def motionsensor_controller_run_for_spi():
    motioncontrol = controller.accel.LIS3DH.SPI(0, 0)
    motioncontrol.start()

    print("Running for 10 seconds...")

    values = motioncontrol.read_for(10)

    print("First 20 results out of {}:".format(len(values)))

    final_results = [[val[0], _format_motionsensor_output(val[1])] for val in values]

    for line in final_results[:20]:
        print(line)

    motioncontrol.stop()


@allow_kbinterrupt
def adc_controller_i2c():
    adc_controller = controller.adc.ADS1015.I2C(0x48, 1)
    adc_controller.set_data_range(4.096)
    adc_controller.start()

    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        print("{} V".format(adc_controller.read()))
        time.sleep(0.1)


@allow_kbinterrupt
def adc_triggers_motionsensor_sensor():
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
        print("Detected high ADC!")
        while time.time() < finish:
            print(_format_motionsensor_output(motionsensor.read()))
            time.sleep(0.1)


@allow_kbinterrupt
def adc_triggers_motionsensor_controller():
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
        print("Detected high ADC!")
        while time.time() < finish:
            print(_format_motionsensor_output(motionsensor.read()))
            time.sleep(0.1)


def main():
    while True:
        print("=" * 30)
        print("Choose a Demo:")
        print("Sensor Class Tests:")
        print("    LIS3DH Tests:")
        print("    1: Test Motionsensor (I2C)")
        print("    2: Test Motionsensor (SPI)")
        print("    ADS1015 Tests:")
        print("    3: Test ADC")
        print("    Combined Tests:")
        print("    4: ADC HIGH triggers motion sensor")
        print("Controller Class Tests")
        print("    LIS3DH Tests:")
        print("    5: Test Motionsensor (I2C)")
        print("    6: Test Motionsensor (SPI)")
        print("    7: Test Motionsensor for 10 seconds (SPI)")
        print("    ADS1015 Tests:")
        print("    8: Test ADC")
        print("Combined Tests:")
        print("    9: ADC HIGH triggers motion sensor")

        print("\n")
        choice = input("Enter choice (q to quit): ")
        if choice == "q":
            break
        elif choice == "1":
            motionsensor_i2c()
        elif choice == "2":
            motionsensor_spi()
        elif choice == "3":
            adc_sensor_i2c()
        elif choice == "4":
            adc_triggers_motionsensor_sensor()
        elif choice == "6":
            motionsensor_controller_spi()
        elif choice == "7":
            motionsensor_controller_run_for_spi()
        elif choice == "8":
            adc_controller_i2c()
        elif choice == "9":
            adc_triggers_motionsensor_controller()


if __name__ == "__main__":
    main()
