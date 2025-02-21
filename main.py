import serial
import time
import datetime
import csv

# Define serial port settings
uart_port = "/dev/ttyS0"  # Change to your serial port (e.g., 'COM3' on Windows)
baud_rate = 9600


def setup():
    print("MH-Z14 CO2 Sensor Test (UART only)")
    # Warm-up period
    print("Warming up the sensor (3 minutes)...")
    for i in range(20):
        print(".", end="", flush=True)
        time.sleep(1)
        if (i + 1) % 60 == 0:
            print()
    print("\nSensor ready!")


def read_co2_uart(ser):
    """
    Read CO2 concentration using UART communication
    Returns CO2 concentration in ppm or -1 if failed
    """
    cmd = bytearray([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
    # Clear input buffer
    ser.reset_input_buffer()
    # Send command to the sensor
    ser.write(cmd)
    # Wait for response
    time.sleep(0.1)

    # Read response
    response = ser.read(9)
    if len(response) == 9:
        print(f"{response}\n")
        # Verify checksum
        checksum = 0
        for i in range(1, 8):
            checksum += response[i]
        checksum = 0xFF - checksum + 1 & 0xFF

        if response[8] == checksum:
            # Extract CO2 value (high byte, low byte)
            response_high = response[2]
            response_low = response[3]
            return (response_high << 8) + response_low
        else:
            print("UART Checksum error!")
            return -1
    else:
        print("No response from sensor (UART)")
        return -1


def calibrate_sensor(ser):
    """
    Calibrate the MH-Z14 sensor to 400ppm (assuming fresh air)
    Note: Only use in fresh outdoor air!
    """
    cmd = bytearray([0xFF, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78])
    # Send calibration command
    ser.write(cmd)
    print("Calibration command sent. Sensor should be in fresh air (~400ppm)")


def set_range(ser, range_value):
    """
    Set the detection range of the sensor
    Options: 2000ppm or 5000ppm (default)
    """
    cmd = bytearray(9)
    if range_value == 2000:
        cmd = bytearray([0xFF, 0x01, 0x99, 0x00, 0x00, 0x00, 0x07, 0xD0, 0x8F])
    else:  # 5000ppm (default)
        cmd = bytearray([0xFF, 0x01, 0x99, 0x00, 0x00, 0x00, 0x13, 0x88, 0xCB])

    ser.write(cmd)
    print(f"Detection range set to {range_value} ppm")


def saveData(data):
    try:
        with open("/home/pi/coopsoil/static/data/co2_data.csv", "a") as file:
            csv.writer(file, delimiter=";").writerow(data)
            file.close()
    except csv.Error as e:
        print(f"Write data error: {str(e)}")


def main():
    # Setup
    setup()
    # Initialize serial port
    try:
        ser = serial.Serial(uart_port, baud_rate, timeout=1)
        print(f"Serial port {uart_port} opened successfully")
    except serial.SerialException as e:
        print(f"Failed to open serial port: {e}")
        return

    # Test sensor response
    print("Testing sensor response...")
    time.sleep(1)
    test_reading = read_co2_uart(ser)
    if test_reading > 0:
        print(f"Sensor responding! Initial reading: {test_reading} ppm")
    else:
        print("WARNING: Sensor not responding via UART")

    try:
        while True:
            # Read CO2 value
            co2ppm = read_co2_uart(ser)
            data = [str(datetime.datetime.now()).split(".")[0], co2ppm]
            saveData(data)
            # Display reading
            if co2ppm > 0:
                print(f"CO2 Concentration: {co2ppm} ppm")
                # Optional: Add threshold warnings
                if co2ppm < 400:
                    print("Warning: CO2 reading is unusually low. Check sensor.")
                elif co2ppm > 1500:
                    print("Warning: CO2 levels elevated. Consider ventilation.")
                elif co2ppm > 5000:
                    print(
                        "Warning: CO2 reading is very high. Ensure proper ventilation!"
                    )
            else:
                print("Failed to read CO2 concentration")

            print("---------------------------")
            time.sleep(5)  # Wait 5 seconds between readings

    except KeyboardInterrupt:
        print("\nExiting program")
    finally:
        # Clean up
        ser.close()
        print("Serial port closed")


if __name__ == "__main__":
    main()
