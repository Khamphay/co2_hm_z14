import serial
import time

ser = serial.Serial("/dev/ttyS0", 9600, timeout=1)


def read_co2():
    command = bytearray([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
    ser.write(command)
    time.sleep(0.1)
    response = ser.read(9)

    if len(response) == 9 and response[0] == 0xFF and response[1] == 0x86:
        co2_value = response[2] * 256 + response[3]
        return co2_value
    else:
        return None


while True:
    co2 = read_co2()
    if co2:
        print(f"CO2 Concentration: {co2} ppm")
    else:
        print("Failed to read CO2 sensor")
    time.sleep(2)
