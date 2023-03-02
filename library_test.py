from edge_ai.sensor import LIS3DH

def main():
    print("Testing Motion Sensor Values: (reading 5 values)")
    motionsensor = LIS3DH.SPI(0, 0, debug = True)
    motionsensor.datarate = 5376
    motionsensor.start()
    
    for _ in range(5):
        print(motionsensor.read())
    
    print("Finished recording")
    motionsensor.stop()

if __name__ == '__main__':
    main()