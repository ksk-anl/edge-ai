import math
import time
import argparse

from edge_ai.sensor.accel import LIS3DH
from edge_ai.sensor.adc import ADS1015

def test_i2c_motion_sensor():
    pass

def test_spi_motion_sensor():
    print("Testing Motion Sensor Values:")
    motionsensor = LIS3DH.SPI(0, 0)
    motionsensor.datarate = 5376
    motionsensor.enable_axes()
    motionsensor.selftest('low')

    motionsensor.start()

    while True:
    # for _ in range(200):
        values = motionsensor.read()
        
        final_value = math.sqrt(sum([x**2 for x in values]))
        
        print(final_value)
        
        time.sleep(0.1)
    
    print("Finished recording")
    motionsensor.stop()
    
def test_adc():
    adc = ADS1015()
    adc.start()
    
    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        print(f"{adc.read()} V")
        time.sleep(0.1)
    
def adc_ping_when_above_thresh():
    adc = ADS1015()
    adc.start()
    THRESH = 2.5
    
    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        if adc.read() > THRESH:
            print(f"Found data above {THRESH} V!")
        time.sleep(0.1)
    
def adc_triggers_motionsensor():
    motionsensor = LIS3DH.SPI(0, 0)
    motionsensor.datarate = 5376
    motionsensor.enable_axes()

    adc = ADS1015()

    motionsensor.start()
    adc.start()
    THRESH = 2.5
    
    while True:
        print("Waiting for ADC to go high before recording motion...")
        
        if adc.read > THRESH:
            print(f'Detected high ADC! motionsensor reading: {motionsensor.read()}')

        time.sleep(0.1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', 
                        choices=['1', '2', '3', '4'],
                        help= 'Choose a mode/sensor to test: 1: i2c motionsensor, 2: spi motionsensor, 3: ADC (analog sensor), 4: ADC ping when above 2.5')
    
    args = parser.parse_args()
    
    if args.mode == '1':
        test_i2c_motion_sensor()
    elif args.mode == '2':
        test_spi_motion_sensor()
    elif args.mode == '3':
        test_adc()
    elif args.mode == '4':
        adc_ping_when_above_thresh()
    elif args.mode == '5':
        adc_triggers_motionsensor()

if __name__ == '__main__':
    main()