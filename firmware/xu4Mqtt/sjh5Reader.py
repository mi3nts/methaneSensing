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
loopInterval = 5




# Command components
IP                    = 0x11  # Fixed IP address
ACK_SUCCESS           = 0x16
ACK_ERROR             = 0x06
BYTE_LENGTH           = 0x01  # Length byte excluding CS
# Commands 
CMD_CHECK_MEASUREMENT   = 0x01
CMD_SW_VERSION          = 0x1E
CMD_INSTRUMENT_NUMBER   = 0x1F
CMD_MEASURMENT_PROPERTY = 0x0D


def main():
    startTime = time.time() 

    ser = serial.Serial(
    port= methanePort,\
    baudrate=baudRate,\
    parity  =serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

    time.sleep(1)

    print("connected to: " + ser.portstr)

    read_instrument_number(ser)
    read_software_number(ser)
    read_measurment_properties(ser)
    read_gas_concentration(ser)

    #this will store the line
    line = []
    while True:
        try:
            read_gas_concentration(ser)
            startTime = mSR.delayMints(time.time() - startTime,loopInterval)

        except Exception as e:
            print(f"Incomplete read. Error: {e}")
            time.sleep(1)
            # Exit the loop if an error occurs

                    
    ser.close()

def send_command(command,ser):
    try:
        command_data = [IP, BYTE_LENGTH, command]
        checksum = calculate_checksum(command_data)
        send_command = command_data + [checksum]
        ser.write(bytearray(send_command))
        time.sleep(.1) 
        response = ser.read(20)
        print(f"Response received:") 
        ack = response[0]
        time.sleep(.1)
        if ack == ACK_SUCCESS :
            print()
            return True, response

        elif ack == ACK_ERROR:
            error_code = response[3]
            print(f"Error: Command not implemented correctly. Error code: {hex(error_code)}")
            return False, response
        else:
            print("Unexpected response.")
            return False, response

    except Exception as e:
        print(f"Incomplete read. Error: {e}")




def calculate_checksum(data: list) -> int:
    """
    Calculate the checksum (CS) as the two's complement of the sum of data bytes.
    """
    return (-sum(data)) & 0xFF

def read_gas_concentration(ser):
    dateTime = datetime.datetime.now()
    validity  , response = send_command(CMD_CHECK_MEASUREMENT,ser)
    if validity:
        df1, df2 = response[3], response[4]
        gas_concentration = (df1 * 256 + df2) / 100.0
        status1 =  response[5]
        print("============================")
        print("= Methan Sensor Data Found =")

        sensorDictionary = OrderedDict([
            ("dateTime", str(dateTime)),
            ("methane",            gas_concentration),  
            ("warmUpStatus",       status1 & 0x01),  
            ("malFunctionStatus",  status1 & 0x02),  
            ("rangeStatus",        status1 & 0x04), 
            ("calibrationStatus",  status1 & 0x10), 
            ("highHumidityStatus", status1 & 0x20), 
            ("RCDOverLimitStatus", status1 & 0x40), 
            ("MCDOverLimitStatus", status1 & 0x80), 
                    ])
        pprint(sensorDictionary)
        mSR.sensorFinisher(dateTime,"SJH5",sensorDictionary)



def decode_status(status1):
    print("Decoding Status")
    status_info = [
        f"Sensor Warm-up Status: {'Warming up' if status1 & 0x01 else 'Completed'}",
        f"Sensor Malfunction Status: {'Malfunction' if status1 & 0x02 else 'Normal'}",
        f"Sensor Display Outrange Status: {'Out of Range' if status1 & 0x04 else 'Within Range'}",
        f"Sensor Calibration Status: {'Not Calibrated' if status1 & 0x10 else 'Calibrated'}",
        f"High Humidity Alarm State: {'High Humidity Alert' if status1 & 0x20 else 'Normal Humidity'}",
        f"Reference Channel Display Over Limit: {'Over Limit' if status1 & 0x40 else 'Within Limit'}",
        f"Measurement Channel Display Over Limit: {'Over Limit' if status1 & 0x80 else 'Within Limit'}"
    ]

    print(status_info)
    print()



def read_instrument_number(ser):
    print("Requesting Instument Number")
    validity  , response = send_command(CMD_INSTRUMENT_NUMBER,ser)
    if validity:
        serial_number_parts = [response[i] for i in range(3, 8)]
        serial_number = "".join(f"{sn:04}" for sn in serial_number_parts)
        print(f"Instrument Serial Number: {serial_number}")

def read_software_number(ser):
    print("Requesting Software Version")
    validity  , response = send_command(CMD_SW_VERSION,ser)
    if validity:
        version_length = response[1] - 1  # Excluding the CMD byte
        version_data = response[3:3 + version_length]
        version_string = ''.join(chr(byte) for byte in version_data)
        print(f"Software Version: {version_string}")


def read_measurment_properties(ser):
    print("Requesting Measurment Property")
    validity, response = send_command(CMD_MEASURMENT_PROPERTY,ser)
    if validity:
        df_values = response[3:10]
        measurement_range = (df_values[0] * 256 + df_values[1]) / (10 ** df_values[2])
        gas_type_code = df_values[3]
        unit_code = df_values[4]

        # Interpret gas type
        gas_types = {
            0: "CH4/C3H8/CBrH3",
            1: "CO2",
            2: "Reserved",
            3: "Reserved"
        }
        gas_type = gas_types.get(gas_type_code, "Unknown")

        # Interpret unit
        units = {
            0: "ppm",
            1: "%",
            2: "%",
            3: "%"
        }
        unit = units.get(unit_code, "Unknown")

        print(f"Measurement Range: {measurement_range} {unit}")
        print(f"Gas Type: {gas_type}")


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print(f"Monitoring Methane Sensor on port: {methanePort} with baudrate {baudRate}")
    main()