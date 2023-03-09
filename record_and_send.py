import io
import time
import math
import datetime

import psycopg2
import pandas as pd

from edge_ai.controller.accel import LIS3DH
from edge_ai.controller.adc import ADS1015

TIMEFORMAT = '%Y-%m-%d %H:%M:%S.%f'

# Postgres DB Access information
RDBACCESS = {
    'dbname': 'edge',
    'user'  :   'postgres',
    'password': 'postgres',
    'host': '192.168.0.38',
    'port': '5432'
}
DEVICE_ID = 1

ADC_THRESHOLD = 2.5
NUMBER_OF_MEASUREMENTS = 20

def main():

    motionsensor = LIS3DH.SPI(busnum = 0, cs = 0)
    adc = ADS1015.I2C(address = 0x48, busnum = 1)

    # Setup sensors
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()
    motionsensor.start()

    adc.start()

    delta_t = 3

    conn = psycopg2.connect(**RDBACCESS)

    for _ in range(NUMBER_OF_MEASUREMENTS):
        print('Waiting for blockage...')

        while True:
            time.sleep(0.1)
            val = adc.read()
            if val > ADC_THRESHOLD:
                break

        time.sleep(0.25)

        results = []

        time_end = time.time() + delta_t
        while time.time() <= time_end:
            values = motionsensor.read()
            final_value = math.sqrt(sum([x**2 for x in values]))

            results.append([f'{datetime.datetime.now():{TIMEFORMAT}}',final_value])

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