#!/usr/bin/env python3
import serial
import time


class CO2Sensor:
    request = [0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]

    def __init__(self, port="/dev/ttyS0"):
        self.serial = serial.Serial(port=port, timeout=1)

    def get(self):
        self.serial.write(bytearray(self.request))
        response = self.serial.read(9)
        if len(response) == 9:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            return {
                "time": current_time,
                "ppa": (response[2] << 8) | response[3],
                "temp": response[4],
            }
        return -1


def main():
    # other Pi versions might need CO2Sensor('/dev/ttyAMA0')
    sensor = CO2Sensor()
    print(sensor.get())


if __name__ == "__main__":
    main()
