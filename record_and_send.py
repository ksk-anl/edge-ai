# import sensors
import os
import psycopg2
import requests
import time
import datetime
import math
import io

import statistics

import pandas as pd

from psycopg2.extras import execute_batch
from requests.auth import HTTPBasicAuth

from edge_ai.sensor.accel import LIS3DH
from edge_ai.sensor.adc import ADS1015

TIMEFORMAT = '%Y-%m-%d %H:%M:%S.%f'
OUTPUTFOLDER = 'output'
RTSURL = 'http://ec2-52-194-91-137.ap-northeast-1.compute.amazonaws.com/rts/api/v1/services/db_test/write_predictions'
RDBACCESS = {
    'dbname': 'edge',
    'user'  :   'postgres',
    'password': 'postgres',
    'host': '192.168.0.38',
    'port': '5432'
}
DEVICE_ID = 1

def main():
    
    motionsensor = LIS3DH.SPI(busnum = 0, cs = 0)
    adc = ADS1015()
    
    # Setup sensors
    motionsensor.datarate = 5376
    motionsensor.enable_axes()
    motionsensor.start()
    
    THRESH = 2.5
    adc.start()

    delta_t = 3
    
    # Prepare output folder
    if not os.path.exists(OUTPUTFOLDER):
        os.mkdir(OUTPUTFOLDER)
    
    # while True:
    for _ in range(20):
        print('Waiting for blockage...')


        while True:
            time.sleep(0.1)
            val = adc.read()
            if val > THRESH:
                break
        # adc.stop()
        # motionsensor.start()
        
        time.sleep(0.25)
        
        results = []

        time_end = time.time() + delta_t
        while time.time() <= time_end:
            values = motionsensor.read()
            final_value = math.sqrt(sum([x**2 for x in values]))

            results.append([f'{datetime.datetime.now():{TIMEFORMAT}}',final_value])
            
        print(f'Recorded {len(results)} lines!')

        
        # TODO: RDB stuff
        # try to send to RDB/RTS
        conn = psycopg2.connect(**RDBACCESS)
        cursor = conn.cursor()

        # write to section table, get section id
        cursor.execute('INSERT INTO sections (device_id, start_time) VALUES (%s, %s) RETURNING id;', (DEVICE_ID, results[0][0]))
        conn.commit()

        print("Wrote to sections table...")
        
        id = cursor.fetchone()[0]
        # print(id)

        # # write csv
        final = pd.DataFrame(data = {'section_id' : [id] * len(results),
                                     'time'       : [row[0] for row in results], 
                                     'gravity'    : [row[1] for row in results]})
        
        # filename = out[0][0]#.split('.')[0] # get only the whole number part
        
        # filepath = f'{OUTPUTFOLDER}/{filename}.csv'
        
        outfile = io.StringIO()
        
        final.to_csv(outfile, header = False, index = False)
        
        # print(final.head)
        # write data to gravity table
        # execute_batch(cursor,
        #               """
        #               INSERT into gravities (section_id, time, gravity) values (%s, %s, %s)
        #               """,
        #               [tuple(row) for row in final.to_numpy()],
        #               page_size = 1000)
        outfile.seek(0)
        cursor.copy_from(outfile, 'gravities', sep = ',')
        conn.commit()
        
        print("Finished Sending to RDB")
        
        # send id to RTS/server
        
        # TEMP: send data directly to RTS
        
        # stddev = statistics.stdev(final.loc[:,'gravity'])
        # res = requests.post(RTSURL, json = {
        #     'data': [ 
        #         { 'gravity.std deviation' : stddev}
        #         ]
        #     },
        #     auth = HTTPBasicAuth('demo_rts','demo_raspi')
        #     )
        
        # pred = res.json()['data'][0]['prediction(label)']
        # print(pred)

        # cursor.execute('INSERT INTO predictions (section_id, normal) VALUES (%s, %s);', (id, pred == 'normal'))
        # conn.commit()

        cursor.close()
        conn.close()
        
        # motionsensor.stop()
        # adc.start()
        # success = True
        
        # # if successful, delete the csv
        # if success:
        # os.remove(filepath)
        

if __name__ == '__main__':
    main()