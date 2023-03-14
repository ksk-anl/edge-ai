import io
import time
import math
import json
import logging

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
    # Preparing logger
    logging.basicConfig(filename = 'scriptlog.log',
                        format = '[%(asctime)s] %(levelname)s: %(message)s',
                        level = logging.INFO)

    logging.info(f'{" Beginning of script. ":=^100}')

    try:
        # Initialize Sensors
        logging.info('Intializing sensors.')
        motionsensor = LIS3DH.SPI(**MOTIONSENSOR)
        adc = ADS1015.I2C(**ADC)
        logging.info('Sensors Initialized.')

        # Configure sensors
        logging.info('Configuring sensors.')
        motionsensor.set_datarate(5376)
        motionsensor.enable_axes()
        motionsensor.start()

        adc.start()
        logging.info('Sensors Configured.')

        # Initialize Database connection
        logging.info('Connecting to Postgres Database.')
        conn = psycopg2.connect(**RDB_ACCESS)
        logging.info('Successfuly connected to Postgres Database.')

        logging.info('Beginning measurement event loop.')
        for i in range(NUMBER_OF_MEASUREMENTS):
            print('Waiting for blockage...')

            logging.info('Waiting for high ADC reading. (Object Detection)')
            while True:
                time.sleep(ADC_MEASUREMENT_INTERVAL)
                val = adc.read()
                if val > ADC_THRESHOLD:
                    break
            logging.info(f'Object detected. Waiting for {WAIT_TIME} seconds.')

            time.sleep(WAIT_TIME)

            logging.info(f'Instructing motion sensor to read for {WINDOW_LENGTH} seconds.')
            values = motionsensor.read_for(WINDOW_LENGTH, timeformat = TIMEFORMAT)
            results = [[row[0], math.sqrt(sum([x ** 2 for x in row[1]]))] for row in values]

            print(f'Recorded {len(results)} lines!')
            logging.info(f'Finished reading motion sensor. {len(results)} lines recorded.')

            cursor = conn.cursor()

            # write to section table, get section id
            logging.info('Attempting to write to sections database.')
            cursor.execute('INSERT INTO sections (device_id, start_time) VALUES (%s, %s) RETURNING id;', (DEVICE_ID, results[0][0]))
            conn.commit()

            logging.info('Finished writing to sections database.')
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

            logging.info('Attempting to write to gravities database.')
            cursor.copy_from(outfile, 'gravities', sep = ',')
            conn.commit()

            print("Finished Sending to Database")
            logging.info('Finished writing to gravities database.')

            cursor.close()
            logging.info(f'Measurement {i + 1} finished.')
    except Exception as e:
        logging.exception(e)

    logging.info('Shutting sensors down.')
    motionsensor.stop()
    adc.stop()
    logging.info('Sensors shut down, ending script.')

if __name__ == '__main__':
    main()