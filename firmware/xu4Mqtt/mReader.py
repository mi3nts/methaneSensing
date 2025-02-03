import serial
import time
import datetime
from pprint import pprint
from collections import OrderedDict
from mintsXU4 import mintsSensorReader as mSR
# Serial port configuration
methanePort = "/dev/tty.usbserial-0001"  # Replace with your port
# methanePort = "/dev/tty.usbserial-AU0645LQ"  # Replace with your port
baudRate = 9600

def calculate_checksum(data: list) -> int:
    """
    Calculate the checksum (CS) as the two's complement of the sum of data bytes.
    """
    return (-sum(data)) & 0xFF

def main():

    ser = serial.Serial(
    port= methanePort,\
    baudrate=baudRate,\
    parity  =serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

    time.sleep(1)
    delta  = .5
    print("connected to: " + ser.portstr)


    # Command components
    IP = 0x11  # Fixed IP address
    CMD_CHECK_MEASUREMENT = 0x01
    ACK_SUCCESS = 0x16
    NAK_ERROR = 0x06

    # Prepare command to check the measurement result
    LB = 0x01  # Length byte excluding CS
    command_data = [IP, LB, CMD_CHECK_MEASUREMENT]
    checksum = calculate_checksum(command_data)
    send_command = command_data + [checksum]
        
    ser.write(bytearray(send_command))
        

    time.sleep(1)
    # response = ser.read(500).decode(errors="ignore")
    # print(response)
    # # full_command = f"[{command.upper()}]"
    # ser.write(full_command.encode())


    #this will store the line
    line = []
    while True:
        # try:
        for c in ser.read():
            print(c)
            line.append(chr(c))
            if chr(c) == '\n':
                dataString     = (''.join(line)).replace("\r\n","")
                # dateTime  = datetime.datetime.now()
                print(dataString)

                   

                    # line = []
                    # break
        # except:
        #     print("Incomplete String Read")
        #     line = []
                    
    ser.close()



if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print(f"Monitoring Methane Sensor on port: {methanePort} with baudrate {baudRate}")
    main()