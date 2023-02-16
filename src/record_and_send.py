import sensors
import os
import psycopg2
import requests
import time

import pandas as pd

from psycopg2.extras import execute_batch
from requests.auth import HTTPBasicAuth

OUTPUTFOLDER = 'output'
RTSURL = ''
RDBACCESS = {
    'dbname': 'edge',
    'user'  :   'postgres',
    'password': 'postgres',
    'host': '192.168.0.32',
    'port': '5432'
}
DEVICE_ID = 1

def main():
    
    motionsensor = sensors.LIS3DH_SPI(busnum = 0, cs = 0)
    adc = sensors.LightSensor()
    
    if not os.path.exists(OUTPUTFOLDER):
        os.mkdir(OUTPUTFOLDER)
    
    while True:
        print('Waiting for blockage...')
        adc.run_until_detected()
        
        time.sleep(0.5)
        
        out = motionsensor.run_for(3)
        print(f'Recorded {len(out)} lines! Back to waiting for blockage.')

        
        # TODO: RDB stuff
        # try to send to RDB/RTS
        conn = psycopg2.connect(**RDBACCESS)# stuff
        cursor = conn.cursor()

        # write to section table, get section id
        cursor.execute('INSERT INTO sections (device_id, start_time) VALUES (%s, %s) RETURNING id;', (DEVICE_ID, out[0][0]))
        conn.commit()
        
        id = cursor.fetchone()[0]
        # print(id)

        # # write csv
        final = pd.DataFrame(data = {'section_id' : [id] * len(out),
                                     'time'       : [row[0] for row in out], 
                                     'gravity'    : [row[1] for row in out]})
        
        # filename = out[0][0].split('.')[0] # get only the whole number part
        
        # filepath = f'{OUTPUTFOLDER}/{filename}.csv'
        
        # final.to_csv(filepath)
        
        # print(final.head)
        # write data to gravity table
        execute_batch(cursor,
                      """
                      INSERT into gravities (section_id, time, gravity) values (%s, %s, %s)
                      """,
                      [tuple(row) for row in final.to_numpy()])
        conn.commit()
        
        # send id to RTS/server
        # res = requests.post(RTSURL, json = {
        #     'data': [{'y.sum':total}]},
        #     # timeout = 5,
        #     auth = HTTPBasicAuth('demoksk','demoksk_pass')
        #     )
        
        # success = True
        
        # # if successful, delete the csv
        # if success:
        #     os.remove(filepath)
        

if __name__ == '__main__':
    main()