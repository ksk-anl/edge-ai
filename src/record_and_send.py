import sensors
import os
import psycopg2

import pandas as pd

from psycopg2.extras import execute_batch

def main():
    OUTPUTFOLDER = 'output'
    
    motionsensor = sensors.LIS3DH_SPI(busnum = 0, cs = 0)
    adc = sensors.LightSensor()
    
    if not os.path.exists(OUTPUTFOLDER):
        os.mkdir(OUTPUTFOLDER)
    
    while True:
        adc.run_until_detected()
        
        out = motionsensor.run_for(3)
        print(f'Recorded {len(out)} lines! Back to waiting for blockage.')

        
        # TODO: RDB stuff
        # try to send to RDB/RTS
        conn = psycopg2.connect()# stuff
        cursor = conn.cursor()

        # write to section table, get section id
        cursor.execute(f'INSERT INTO section (device_id, start_time) VALUES ({DEVICE_ID}, {out[0][0]});')
        conn.commit()
        
        id = cursor.fetchone()[0]

        # write csv
        final = pd.DataFrame(data = {'section_id' : [id] * len(out),
                                     'unixtime'   : [row[0] for row in out], 
                                     'gravity'    : [row[1] for row in out]})
        
        filename = out[0][0].split('.')[0] # get only the whole number part
        
        filepath = f'{OUTPUTFOLDER}/{filename}.csv'
        
        final.to_csv(filepath)
        
        # write data to gravity table
        execute_batch(cursor,
                      """
                      INSERT into gravity(section_id, unixtime, gravity) values (%s, %s, %s)
                      """,
                      [tuple(row) for row in final.to_numpy()])
        
        conn.commit()
        
        # send id to RTS/server
        
        success = True
        
        # if successful, delete the csv
        if success:
            os.remove(filepath)
        

if __name__ == '__main__':
    main()