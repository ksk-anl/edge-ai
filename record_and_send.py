import io
import time
import math
import json
import datetime

import psycopg2
import pandas as pd

from edge_ai.controller.accel import LIS3DH
from edge_ai.controller.adc import ADS1015

TIMEFORMAT = '%Y-%m-%d %H:%M:%S.%f'

# Postgres DB Access information
# RDBACCESS = {
#     'dbname': 'edge',
#     'user'  :   'postgres',
#     'password': 'postgres',
#     'host': '192.168.0.38',
#     'port': '5432'
# }
with open("config.json") as f:
    config = json.loads(f)
    RDBACCESS = config['rdb_access']

    DEVICE_ID = config['device_id']

    ADC_THRESHOLD = config['adc_threshold']
    NUMBER_OF_MEASUREMENTS = config['measurements']

    MOTIONSENSOR = config['motionsensor_spi']
    ADC = config['adc_i2c']

    MEASUREMENT_WINDOW = config['window_length']
    WAIT_TIME = config['wait_time']
    ADC_MEASUREMENT_INTERVAL = config['adc_measurement_interval']

def main():

    motionsensor = LIS3DH.SPI(**MOTIONSENSOR)
    adc = ADS1015.I2C(**ADC)

    # Setup sensors
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()
    motionsensor.start()

    adc.start()

    conn = psycopg2.connect(**RDBACCESS)

    for _ in range(NUMBER_OF_MEASUREMENTS):
        print('Waiting for blockage...')

        while True:
            time.sleep(ADC_MEASUREMENT_INTERVAL)
            val = adc.read()
            if val > ADC_THRESHOLD:
                break

        time.sleep(WAIT_TIME)

        results = []

        time_end = time.time() + MEASUREMENT_WINDOW
        while time.time() <= time_end:
            values = motionsensor.read()
            final_value = math.sqrt(sum([x ** 2 for x in values]))

            results.append([f'{datetime.datetime.now():{TIMEFORMAT}}', final_value])

        print(f'Recorded {len(results)} lines!')

        cursor = conn.cursor()

        # write to section table, get section id
        cursor.execute('INSERT INTO sections (device_id, start_time) VALUES (%s, %s) RETURNING id;', (DEVICE_ID, results[0][0]))
        conn.commit()

        print("Finished writing to sections table...")

        id = cursor.fetchone()[0]

        # write csv
        final = pd.DataFrame(data = {'section_id' : [id] * len(results),
                                     'time'       : [row[0] for row in results],
                                     'gravity'    : [row[1] for row in results]})

        outfile = io.StringIO()

        final.to_csv(outfile, header = False, index = False)

        # write data to gravities table
        outfile.seek(0)
        cursor.copy_from(outfile, 'gravities', sep = ',')
        conn.commit()

        print("Finished Sending to RDB")

        cursor.close()

if __name__ == '__main__':
    main()