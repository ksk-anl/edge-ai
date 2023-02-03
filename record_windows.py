import smbus2
import time
import datetime
import math
import pandas as pd
import argparse
import os
import requests
from requests.auth import HTTPBasicAuth
import spidev

import Adafruit_ADS1x15
import multiprocessing as mp

# TODO: set timezone to always be Asia/Tokyo
TIMEFORMAT = '%H:%M:%S.%f'
# RTSURL = 'http://ec2-52-194-91-137.ap-northeast-1.compute.amazonaws.com/rts/api/v1/services/rail/score'

def read_i2c_motionsensor(i2c : smbus2.SMBus, address):#, writer):
    #データ読み込み
    xl = i2c.read_byte_data(address, 0x29)
    yl = i2c.read_byte_data(address, 0x2B)
    zl = i2c.read_byte_data(address, 0x2D)

    return (xl, yl, zl)

def read_spi_motionsensor(spi):
    x_dat = [0x00, 0x00]
    y_dat = [0x00, 0x00]
    z_dat = [0x00, 0x00]
    
    #読み込み設定
    x_dat[0] = 0x28
    x_dat[0] |= 0x80
    x_dat[0] |= 0x40

    y_dat[0] = 0x2A
    y_dat[0] |= 0x80
    y_dat[0] |= 0x40

    z_dat[0] = 0x2C
    z_dat[0] |= 0x80
    z_dat[0] |= 0x40

    #データ読み込み
    readByteArry = spi.xfer2(x_dat)
    readByteArry = spi.xfer2(y_dat)
    readByteArry = spi.xfer2(z_dat)
    
    print(f'x {x_dat}, y {y_dat}, z {z_dat}')

    return (x_dat[1], y_dat[1], z_dat[1])
    
    
def calc_n(xl,  yl, zl):# = readings
    #データ変換
    
    out_x = xl
    out_y = yl
    out_z = zl

    BITS = 8
    max_val = 2**BITS
    
    #極性判断
    if out_x >= max_val/2.:
        out_x -= max_val
    
    if out_y >= max_val/2.:
        out_y -= max_val

    if out_z >= max_val/2.:
        out_z -= max_val

    #物理量（加速度）に変換
    out_x = float(out_x) / (max_val/4.)
    out_y = float(out_y) / (max_val/4.)
    out_z = float(out_z) / (max_val/4.)
    
    n = math.sqrt(out_x**2 + out_y**2 + out_z**2)

    return [f'{datetime.datetime.now():{TIMEFORMAT}}', n]

def main():
    # parse output filename
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument('number_of_windows')
    parser.add_argument('time_per_window')
    args = parser.parse_args()

    OUTPUTFOLDER = args.output
    if not os.path.exists(OUTPUTFOLDER):
        os.mkdir(OUTPUTFOLDER)

    # ----------- For I2C Motion Sensor -----------
    #I2C設定
    i2c = smbus2.SMBus(1)
    address = 0x19

    #LIS3DH設定
    i2c.write_byte_data(address, 0x20, 0b10011111)

    # #self-test HIGH
    # i2c.write_byte_data(address, 0x23, 0b00000100)

    # #self-test LOW
    # i2c.write_byte_data(address, 0x23, 0b00000010)

    # # ----------- For SPI Motion Sensor -----------
    # # setup SPI LIS3DH
    # spi = spidev.SpiDev()
    # spi.open(0, 0)
    # spi.max_speed_hz = 10000
    # spi.mode = 3

    # s_dat = [0x00, 0x00]
    # #LIS3DH設定
    # s_dat[0] = 0x20
    # s_dat[1] = 0b10011111
    # readByteArry = spi.xfer2(s_dat)

    # setup ADC
    ADC_GAIN = 1
    adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum = 1)

    count = 0
    # window_count = 0
    delta_t = float(args.time_per_window)
    filenum = 0
    diff = 0
    THRESH = 2.5 # Volts


    #繰り返し
    # while true
    
        # if the sensor gets interrupted:
        # window_count += 1

    while filenum < int(args.number_of_windows):
        # wait for light sensor interrupt
        
        while diff < THRESH:
            diff = adc.read_adc_difference(0, gain = ADC_GAIN)
            diff = diff *4.096*2/4096
            time.sleep(0.1)
        
        # print(f'Block detected, recording for the next {args.time_per_window} seconds.')
        
        results = []
        # record window
        t_end = time.time() + delta_t
        while time.time() <= t_end:
            readings = read_i2c_motionsensor(i2c, address)
            # readings = read_spi_motionsensor(spi)
            # print(readings)
            results.append(calc_n(*readings))
            count += 1

        final = pd.DataFrame(data = {'time': [row[0] for row in results], 
                                     'y'   : [row[1] for row in results]})

        # if the file already exists, try to save in the next filename
        while os.path.exists(f'{OUTPUTFOLDER}/out{filenum:03}.csv'):
            filenum += 1

        final.to_csv(f'{OUTPUTFOLDER}/out{filenum:03}.csv', index=False)
        print(f'Saved file {filenum:03}...')
        filenum += 1
        
    # spi.close()
    i2c.close()
        
    print(f"Recorded {count} lines in {delta_t*float(args.number_of_windows)} seconds. ({count*1.0/delta_t} Hz)")

    # # process results here
    # print(results[:3])

if __name__ == '__main__':
    main()