from edge_ai.sensor import LIS3DH

def main():
    print("Testing Motion Sensor Values: (reading 200 values)")
    motionsensor = LIS3DH.SPI(0, 0)
    motionsensor.datarate = 5376
    motionsensor.axes = (True, True, True)
    motionsensor.start()
    
    # for _ in range(200):
    while True:
        print(motionsensor.read())
    
    print("Finished recording")
    motionsensor.stop()

if __name__ == '__main__':
    main()