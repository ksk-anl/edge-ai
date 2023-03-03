# import sensors
import os
import psycopg2
import requests
import time
import datetime
import math

import statistics

import pandas as pd

from psycopg2.extras import execute_batch
from requests.auth import HTTPBasicAuth

import edge_ai.sensor as sensors

TIMEFORMAT = '%Y-%m-%d %H:%M:%S.%f'
OUTPUTFOLDER = 'output'
RTSURL = 'http://ec2-52-194-91-137.ap-northeast-1.compute.amazonaws.com/rts/api/v1/services/db_test/write_predictions'
RDBACCESS = {
    'dbname': 'edge',
    'user'  :   'postgres',
    'password': 'postgres',
    'host': '192.168.0.32',
    'port': '5432'
}
DEVICE_ID = 1

def main():
    
    motionsensor = sensors.accel.LIS3DH.SPI(busnum = 0, cs = 0)
    adc = sensors.adc.ADS1015()
    
    # Setup sensors
    motionsensor.datarate = 5376
    motionsensor.enable_axes()
    motionsensor.start()
    
    adc.start()
    THRESH = 2.5
    delta_t = 3
    
    if not os.path.exists(OUTPUTFOLDER):
        os.mkdir(OUTPUTFOLDER)
        
    
    while True:
        print('Waiting for blockage...')
        
        while adc.read() < THRESH:
            pass
        
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
        
        # final.to_csv(filepath)
        
        # print(final.head)
        # write data to gravity table
        execute_batch(cursor,
                      """
                      INSERT into gravities (section_id, time, gravity) values (%s, %s, %s)
                      """,
                      [tuple(row) for row in final.to_numpy()])
        # with open(filepath, 'r') as f:
        #     conn.copy_from(f, 'gravities', sep = ',')
        conn.commit()
        
        print("Finished Sending to RDB")
        
        # send id to RTS/server
        
        # TEMP: send data directly to RTS
        
        stddev = statistics.stdev(final.loc[:,'gravity'])
        res = requests.post(RTSURL, json = {
            'data': [ 
                { 'gravity.std deviation' : stddev}
                ]
            },
            auth = HTTPBasicAuth('demo_rts','demo_raspi')
            )
        
        pred = res.json()['data'][0]['prediction(label)']
        print(pred)

        cursor.execute('INSERT INTO predictions (section_id, normal) VALUES (%s, %s);', (id, pred == 'normal'))
        conn.commit()

        cursor.close()
        conn.close()
        # success = True
        
        # # if successful, delete the csv
        # if success:
        # os.remove(filepath)
        

if __name__ == '__main__':
    main()