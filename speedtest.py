import time

import edge_ai.controller as controller

TEST_TIME = 10.

def main() -> None:
    motionsensor = controller.accel.LIS3DH.SPI(0, 0, maxspeed= 10_000_000)
    motionsensor.start()
    print(f"read() for {TEST_TIME} seconds")

    start = time.time()
    records = 0
    while time.time() < start + TEST_TIME:
        motionsensor.read()
        records += 1

    print("Simple read:", end=" ")
    print(f"Recorded {records} lines in {TEST_TIME} seconds! {(records * 1.0) / TEST_TIME} Hz")

    read_for_results = motionsensor.read_for(TEST_TIME)

    print("read_for:", end=" ")
    print(f"Recorded {len(read_for_results)} lines in {TEST_TIME} seconds! {(len(read_for_results) * 1.0) / TEST_TIME} Hz")

    motionsensor.stop()

if __name__ == "__main__":
    main()