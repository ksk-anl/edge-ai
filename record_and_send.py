import io
import time
import math
import json
import datetime

import psycopg2
import pandas as pd

from edge_ai.controller.accel import LIS3DH
from edge_ai.controller.adc import ADS1015

with open("config.json") as f:
    config = json.load(f)

    # Formatting constants
    TIMEFORMAT = config['timeformat']

    # Database Access constants
    RDB_ACCESS = config['rdb_access']
    DEVICE_ID = config['device_id']

    # Sensor Interface configurations
    MOTIONSENSOR = config['motionsensor_spi']
    ADC = config['adc_i2c']

    # Script variables
    ADC_THRESHOLD = config['adc_threshold']
    ADC_MEASUREMENT_INTERVAL = config['adc_measurement_interval']
    NUMBER_OF_MEASUREMENTS = config['number_measurements']
    WINDOW_LENGTH = config['window_length']
    WAIT_TIME = config['wait_time']

def main() -> None:
    # Initialize Sensors
    motionsensor = LIS3DH.SPI(**MOTIONSENSOR)
    adc = ADS1015.I2C(**ADC)

    # Configure sensors
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()
    motionsensor.start()

    adc.start()

    # Initialize Database connection
    conn = psycopg2.connect(**RDB_ACCESS)

    for _ in range(NUMBER_OF_MEASUREMENTS):
        print('Waiting for blockage...')

        while True:
            time.sleep(ADC_MEASUREMENT_INTERVAL)
            val = adc.read()
            if val > ADC_THRESHOLD:
                break

        time.sleep(WAIT_TIME)

        values = motionsensor.read_for(WINDOW_LENGTH, timeformat = TIMEFORMAT)
        results = [[row[0], math.sqrt(sum([x ** 2 for x in row[1]]))] for row in values]

        print(f'Recorded {len(results)} lines!')

        cursor = conn.cursor()

        # write to section table, get section id
        cursor.execute('INSERT INTO sections (device_id, start_time) VALUES (%s, %s) RETURNING id;', (DEVICE_ID, results[0][0]))
        conn.commit()

        print("Finished writing to sections table...")

        id = cursor.fetchone()[0]

        # Arrange data into correct columns
        final = pd.DataFrame(data = {'section_id' : [id] * len(results),
                                     'time'       : [row[0] for row in results],
                                     'gravity'    : [row[1] for row in results]})

        # Load data into a file-like object for copying
        outfile = io.StringIO()
        final.to_csv(outfile, header = False, index = False)

        # write data to gravities table
        outfile.seek(0)
        cursor.copy_from(outfile, 'gravities', sep = ',')
        conn.commit()

        print("Finished Sending to Database")

        cursor.close()

    motionsensor.stop()
    adc.stop()

if __name__ == '__main__':
    main()