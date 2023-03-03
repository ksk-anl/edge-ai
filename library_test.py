import math
import argparse

from edge_ai.sensor import LIS3DH, ADS1015

def test_i2c_motion_sensor():
    pass

def test_spi_motion_sensor():
    print("Testing Motion Sensor Values: (reading 200 values)")
    motionsensor = LIS3DH.SPI(0, 0)
    motionsensor.datarate = 5376
    motionsensor.enable_axes()
    motionsensor.selftest('low')

    motionsensor.start()

    for _ in range(200):
        values = motionsensor.read()
        
        final_value = math.sqrt(sum([x**2 for x in values]))
        
        print(final_value)
    
    print("Finished recording")
    motionsensor.stop()
    
def test_adc():
    adc = ADS1015()
    adc.start()
    
    print("Outputting ADC output, Ctrl + C to stop:")
    while True:
        print(f"{adc.read()} V")
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', 
                        choices=['1', '2', '3'],
                        help= 'Choose a mode/sensor to test: 1: i2c motionsensor, 2: spi motionsensor, 3: ADC (analog sensor)')
    
    args = parser.parse_args()
    
    if args.mode == '1':
        test_i2c_motion_sensor()
    elif args.mode == '2':
        test_spi_motion_sensor()
    elif args.mode == '3':
        test_adc()

if __name__ == '__main__':
    main()