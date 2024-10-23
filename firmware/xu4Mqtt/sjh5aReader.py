#
import serial
import datetime
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
import sys
import time
# dataFolder  = mD.dataFolder
# ipsPort     = "/dev/ttyS0"
# baudRate    = 115200

# Setup serial connection (adjust the port and baudrate if necessary)
ser = serial.Serial(
    port="/dev/ttyS0",  # Use the correct serial port for your Raspberry Pi
    baudrate=9600,
    timeout=1
)

# Function to calculate the checksum (CS)
def calculate_checksum(data):
    return (-sum(data)) & 0xFF  # Modulo 256 (one-byte checksum)

# Function to send a command to the sensor
def send_command(command):
    ser.write(bytearray(command))

# Function to read a response from the sensor
def read_response():
    response = ser.read(9)  # Adjust the length if necessary
    return list(response)

# Function to check the measurement result
def check_measurement():
    # Command: [IP] [LB] [CMD] [CS]  (0x11 0x01 0x01 0xED)
    command = [0x11, 0x01, 0x01]  # IP=11, LB=1, CMD=1
    checksum = calculate_checksum(command)
    command.append(checksum)

    # Send the command
    send_command(command)

    # Read the response
    response = read_response()
    print(response)
    if len(response) == 8:
        # Parse the response
        if response[0] == 0x16:  # ACK
            # Gas concentration: (DF1 * 256 + DF2) / 100
            df1 = response[3]
            df2 = response[4]
            gas_concentration = (df1 * 256 + df2) / 100.0

            # Sensor status (ST1, ST2)
            st1 = response[5]
            st2 = response[6]

            print(f"Gas Concentration: {gas_concentration} ppm")
            print(f"Sensor Status: ST1={st1}, ST2={st2}")
        else:
            print("Error: NAK received or unknown response")
    else:
        print("Error: Invalid response length")


if __name__ == "__main__":
    try:
        while True:
            check_measurement()
            time.sleep(10);
    
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ser.close()