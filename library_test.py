from edge_ai.sensor import LIS3DH

def main():
    print("Testing Motion Sensor Values: (reading 5 values)")
    motionsensor = LIS3DH.SPI(1, 1, debug = True)
    
    for _ in range(5):
        print(motionsensor.read())

if __name__ == '__main__':
    main()