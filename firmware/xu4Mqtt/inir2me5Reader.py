import serial
import time
import datetime
from pprint import pprint
from collections import OrderedDict
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD

# Serial port configuration
methanePort =   mD.inir2me5Port
baudRate     = 38400
loopInterval = 1 


def main():
    """
    Main function to read data from the methane sensor via the serial port
    and display both ASCII and HEX values, keeping only the last two ASCII characters.
    """
    try:
        # Serial connection setup
        ser = serial.Serial(
            port=methanePort,
            baudrate=baudRate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS,
            timeout=0,
        )
        time.sleep(1)
        print("\nConnected to: " + ser.portstr + "\n")
        time.sleep(1)

        print("Entering Configuration Mode")
        configMode, response   = send_command("C",ser)
        # print(response)
        if(configMode):
            print("In Configuration Mode")

        print("Requesting to read back current settings")
        dateTime = datetime.datetime.now()
        readSettings, response = send_command("I",ser)
        
        if(readSettings):
            print("Printing  Settings")
            printSettings(response,dateTime)

        print("Entering Engineering Mode")
        EngineeringMode, response   = send_command("B",ser)
        print(response)
        if(EngineeringMode):
            print("In Engineering Mode")
            lineASCII = []
            startTimeMacro = time.time()
            startTime      = startTimeMacro
            while True:
                try:
                    # Read bytes from the serial buffer
                    for byte in ser.read():
                        ascii_char = chr(byte)  # if 32 <= byte <= 126 else "."  # Handle printable and non-printable characters
                        lineASCII.append(ascii_char)

                        data = ''.join(lineASCII)
                        lines = data.split("\n\r")
                        lines = [line for line in lines if line.strip()]

                        # print(lines)
                        if lines and lines[-1] == "0000005d":
                            if lines[0] == "0000005b":
                                dateTime = datetime.datetime.now()
                                print(lines)
                                print("============================")
                                print("= Methan Sensor Data Found =")

                                sensorDictionary = OrderedDict([
                                    ("dateTime", str(dateTime)),
                                    ("methane",            int(lines[1], 16)),  
                                    ("faultCode",          int(lines[2], 16)),  
                                    ("temperature",        (int(lines[3], 16)/10)- 273.15),  
                                    ("ref1SecAverage",     int(lines[4], 16)), 
                                    ("act1SecAverage",     int(lines[5], 16)), 
                                    ("crc",                int(lines[6], 16)), 
                                    ("crc1sComp",          int(lines[7], 16)), 
                                            ])
                                pprint(sensorDictionary)
                                
                                if time.time() - startTimeMacro> 60 :
                                    print("Sensor Warmed Up")
                                    mSR.sensorFinisher(dateTime,"INIR2ME5",sensorDictionary)
                                

                                                           
                                lineASCII = []
                                lines     = []

                            startTime = mSR.delayMints(time.time() - startTime,loopInterval)     

                except Exception as e:
                    print(f"Incomplete read. Error: {e}")
                    break  # Exit the loop if an error occurs

    except serial.SerialException as e:
        print(f"Failed to connect to {methanePort}. Error: {e}")


def printSettings(response,dateTime):

    # print(response)
    lineSettings = response.split("\n\r")
    lineSettings   = [lineSettings for lineSettings in lineSettings if lineSettings.strip()]
    if len(lineSettings) == 38:
        settingsDictionary = OrderedDict([
            ("dateTime", str(dateTime)),
            ("sensor_type", int(lineSettings[1], 16)),  # Gas Sensor Type (e.g., INIR-M100%)
            ("gas_type", int(lineSettings[2], 16)),  # Gas Type (e.g., Methane, Propane)
            ("conc_range", int(lineSettings[3], 16)),  # Full Scale Target for Analog Output Calculations
            ("high_span_gas_conc", int(lineSettings[4], 16) / 10000),  # High Span Gas Cylinder Concentration (ppm)
            ("low_span_gas_conc", int(lineSettings[5], 16) / 10000),  # Low Span Gas Cylinder Concentration (ppm)
            ("a_coeff_low_range", int(lineSettings[6], 16) / 1000000),  # "a" Coefficient for Low Range Gas
            ("a_coeff_mid_range", int(lineSettings[7], 16) / 1000000),  # "a" Coefficient for Middle Range Gas
            ("a_coeff_high_range", int(lineSettings[8], 16) / 1000000),  # "a" Coefficient for High Range Gas
            ("n_coeff_low_conc", int(lineSettings[9], 16) / 1000000),  # "n" Coefficient for Low Range Gas
            ("n_coeff_mid_conc", int(lineSettings[10], 16) / 1000000),  # "n" Coefficient for Middle Range Gas
            ("n_coeff_high_conc", int(lineSettings[11], 16) / 1000000),  # "n" Coefficient for High Range Gas
            ("betaneg_coeff_low_range", int(lineSettings[12], 16) / 1000000),  # Negative "beta" Coefficient (Low)
            ("betaneg_coeff_mid_range", int(lineSettings[13], 16) / 1000000),  # Negative "beta" Coefficient (Mid)
            ("betaneg_coeff_high_range", int(lineSettings[14], 16) / 1000000),  # Negative "beta" Coefficient (High)
            ("betapos_coeff_low_range", int(lineSettings[15], 16) / 1000000),  # Positive "beta" Coefficient (Low)
            ("betapos_coeff_mid_range", int(lineSettings[16], 16) / 1000000),  # Positive "beta" Coefficient (Mid)
            ("betapos_coeff_high_range", int(lineSettings[17], 16) / 1000000),  # Positive "beta" Coefficient (High)
            ("alphaneg_coeff", int(lineSettings[18], 16) / 1000000),  # Negative "alpha" Coefficient
            ("alphapos_coeff", int(lineSettings[19], 16) / 1000000),  # Positive "alpha" Coefficient
            ("averaging", int(lineSettings[20], 16)),  # Averaging for Signal Processing
            ("baud_rate", int(lineSettings[21], 16)),  # UART Communication Baud Rate
            ("current_conc_range", int(lineSettings[22], 16)),  # LOW_CONC = 0, MID_CONC = 1, HIGH_CONC = 2
            ("customer_calibration_time", int(lineSettings[23], 16)),  # Calibration Time (hhmmss format)
            ("customer_calibration_date", int(lineSettings[24], 16)),  # Calibration Date (DDMMYY format)
            ("serial_number", int(lineSettings[25], 16)),  # Device Serial Number
            ("time_delay_ms", int(lineSettings[26], 16)),  # Signal Peak Delay (ms)
            ("firmware_version", int(lineSettings[27], 16)),  # Firmware Version
            ("Act_1s_Average_Calibrate", int(lineSettings[28], 16) / 1000000),  # Calibrated 1s Average (Active)
            ("Ref_1s_Average_Calibrate", int(lineSettings[29], 16) / 1000000),  # Calibrated 1s Average (Reference)
            ("zero", int(lineSettings[30], 16) / 1000000),  # Calibrated Zero Value
            ("span", int(lineSettings[31], 16) / 1000000),  # Calibrated Span Value
            ("offset", int(lineSettings[32], 16) / 10000),  # Calculated Offset Concentration (ppm)
            ("calibration_temperature", int(lineSettings[33], 16) / 10),  # Calibration Temperature (Kelvin * 10)
            ("val_crc", int(lineSettings[34], 16)),  # CRC Value
            ("inv_crc", int(lineSettings[35], 16)),  # 1's Complement of CRC
        ])
        pprint(settingsDictionary)
        mSR.sensorFinisher(dateTime,"INIR2ME5SET",settingsDictionary)


def send_command(command,ser):
    if not command.isalpha() or len(command) != 1:
        print("Invalid command. Use a single uppercase letter.")
        return
    # Format the command structure and encode it
    full_command = f"[{command.upper()}]"
    ser.write(full_command.encode())
    response = ser.read(500).decode(errors="ignore")
    time.sleep(1)
    print(f"Sent command: {full_command}")
    time.sleep(1)
    response = ser.read(500).decode(errors="ignore")
    response = response.strip()
    # print(f"Response: {response.strip()}")
    time.sleep(1)
    if response.endswith("5b414b5d"):
        print("Command Accepted")
        return True,response
    else:
        return False,response
        
    # Read response if available
    # response = ser.read(100).decode(errors="ignore")
    # print(f"Response: {response.strip()}")

if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print(f"Monitoring Methane Sensor on port: {methanePort} with baudrate {baudRate}")
    main()