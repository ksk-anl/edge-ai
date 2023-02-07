import sensors
import argparse

def test_i2c_motion_sensor():
    print('Sample I2C Motion Sensor output:')
    motionsensor = sensors.LIS3DH_I2C(busnum = 1, address = 0x19)
    out = motionsensor.run_for(1)
    print(out[0:5])

def test_spi_motion_sensor():
    print('Sample SPI Motion Sensor output:')
    motionsensor = sensors.LIS3DH_SPI(busnum = 0, cs = 0)
    out = motionsensor.run_for(1)
    print(out[0:5])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', 
                        choices=['1', '2', '3'],
                        help= 'Choose a mode/sensor to test: 1: i2c motionsensor, 2: spi motionsensor, 3: i2c ADC')
    
    args = parser.parse_args()
    
    if args.mode == '1':
        test_i2c_motion_sensor()
    elif args.mode == '2':
        test_spi_motion_sensor()

if __name__ == '__main__':
    main()