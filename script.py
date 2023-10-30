import io
import json
import logging
import math
import os
import time
from urllib import request, parse

import pandas as pd
import pymongo
import requests

from edge_ai.controller.accel import LIS3DH
from edge_ai.controller.adc import ADS1015

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def _parse_config():
    # TODO: Parse and validate JSON contents
    with open("{}/config.json".format(BASE_PATH)) as f:
        config = json.load(f)
    return config


def _event_loop(motionsensor, adc, conn, config,):
    logging.info("Waiting for high ADC reading (Object Detection)")
    while True:
        time.sleep(config["adc_measurement_interval"])
        val = adc.read()
        if val > config["adc_threshold"]:
            break
    logging.info('Object detected. Waiting for {} seconds'.format(config["wait_time"]))

    time.sleep(config["wait_time"])

    logging.info(
        'Instructing motion sensor to read for {} seconds'.format(
            config["window_length"]
        )
    )
    values = motionsensor.read_for(
        config["window_length"], timeformat=config["timeformat"]
    )
    results = [[row[0], math.sqrt(sum([x**2 for x in row[1]]))] for row in values]

    logging.info(
        "Finished reading motion sensor. {} lines recorded".format(len(results))
    )

    cursor = conn.cursor()

    # write to section table, get section id
    logging.info("Attempting to write to sections database")
    cursor.execute(
        "INSERT INTO sections (device_id, start_time) VALUES (%s, %s) RETURNING id;",
        (config["device_id"], results[0][0]),
        )
    conn.commit()

    id = cursor.fetchone()[0]
    logging.info("Finished writing to sections database (Section {})".format(id))

    # Arrange data into correct columns
    logging.info("Preparing data for copy")
    final = pd.DataFrame(
        data={
            "section_id": [id] * len(results),
            "time": [row[0] for row in results],
            "gravity": [row[1] for row in results],
        }
    )

    # Load data into a file-like object for copying
    outfile = io.StringIO()
    final.to_csv(outfile, header=False, index=False)

    # Write data to gravities table
    outfile.seek(0)

    logging.info("Attempting to copy data to gravities table")

    # with conn.begin():
    #     res = conn.execute(
    #         "INSERT INTO sections (device_id, start_time) VALUES ({}, {}) RETURNING id;".format(
    #             (config["device_id"], results[0][0])
    #         )
    #     )
    cursor.copy_from(outfile, "gravities", sep=",")
    conn.commit()

    logging.info("Finished writing to gravities table")

    res = None
    if config["rts_url"] != "":

        auth_handler = request.HTTPBasicAuthHandler()
        auth_handler.add_password(realm = None,
                                  uri = config['rts_url'],
                                  user = config['rts_access']['username'],
                                  passwd = config['rts_access']['password'])
        opener = request.build_opener(auth_handler)
        request.install_opener(opener)

        data = parse.urlencode({"data": [{"section_id": id}]}).encode()

        req = request.Request(url = config['rts_url'],
                              data = data,
                              method = 'POST')
        res = request.urlopen(req)

        # res = requests.post(
        #     config["rts_url"],
        #     auth=HTTPBasicAuth(**config["rts_access"]),
        #     json={"data": [{"section_id": id}]},
        # )

        logging.info("Wrote to RTS with response {}".format(res))
    else:
        logging.warning("No RTS URL set. Will not attempt to POST.")

    cursor.close()


def main():
    config = _parse_config()

    # Preparing logger
    logging.basicConfig(
        filename='{}/{}'.format(BASE_PATH, config["logfile"]),
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )

    logging.info('{:=^50}'.format(" Beginning of script "))

    try:
        # Initialize Sensors
        logging.info("Intializing sensors")
        motionsensor = LIS3DH.SPI(**config["motionsensor_spi"])
        adc = ADS1015.I2C(**config["adc_i2c"])
        logging.info("Sensors Initialized")

        # Configure sensors
        logging.info("Configuring sensors")
        motionsensor.set_datarate(5376)
        motionsensor.enable_axes()
        motionsensor.start()

        adc.start()
        logging.info("Sensors Configured")

        # Initialize Database connection
        logging.info("Connecting to Postgres Database")
        engine = sqlalchemy.create_engine(
            "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(**config["rdb_access"])
            )

        # conn = psycopg2.connect(**config["rdb_access"])
        conn = engine.raw_connection()
        logging.info("Successfuly connected to Postgres Database")

        logging.info("Beginning measurement event loop")

        if config["number_measurements"] != "infinite":
            for i in range(config["number_measurements"]):
                _event_loop(motionsensor, adc, conn, config)
                logging.info(
                    'Measurement {} of {} finished'.format(
                        i + 1, config["number_measurements"]
                    )
                )
        else:
            logging.info("Measuring indefinitely...")
            while True:
                _event_loop(motionsensor, adc, conn, config)

    except Exception as e:
        logging.exception(e)

    logging.info("Shutting sensors down")
    motionsensor.stop()
    adc.stop()
    conn.close()
    logging.info("Finishing script")


if __name__ == "__main__":
    main()
