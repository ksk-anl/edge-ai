import time

import edge_ai.controller.accel as accel

def main() -> None:
    motionsensor = accel.LIS3DH.SPI(0, 0)
    motionsensor.set_datarate(5376)
    motionsensor.enable_axes()
    motionsensor.set_selftest('off')

    motionsensor.start()

    TEST_TIME = 10

    start_t = time.time()
    records = 0
    while time.time() < start_t + TEST_TIME:
        motionsensor.read()
        records += 1

    print(f'{records} lines recorded in {TEST_TIME} seconds! ({records*1.0/TEST_TIME}Hz)')
    motionsensor.stop()

if __name__ == '__main__':
    main()