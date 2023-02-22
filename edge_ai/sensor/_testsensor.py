from ..bus._testbus import _TestBus

class _TestSensor():
    def __init__(self) -> None:
        print("Starting Test Sensor Initialization... \nImporting TestBus from neighboring folder")
        bus = _TestBus()
        print("This sensor has initialized")