from edge_ai.sensor import LIS3DH

def main():
    print("Testing Motion Sensor Values: (reading 200 values)")
    motionsensor = LIS3DH.SPI(0, 0)
    motionsensor.datarate = 5376
    motionsensor.start()
    
    for _ in range(200):
        print(motionsensor.read())
    
    print("Finished recording")
    motionsensor.stop()

if __name__ == '__main__':
    main()