#
import serial
import datetime
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
import sys
import time
import board
import busio
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219


i2c_bus = board.I2C(0x41)  # uses board.SCL and board.SDA
# i2c_bus = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

ina219 = INA219(i2c_bus)


if __name__ == "__main__":
    try:
        while True:
            print("ina219 test")
            bus_voltage = ina219.bus_voltage  # voltage on V- (load side)
            shunt_voltage = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
            current = ina219.current  # current in mA
            power = ina219.power  # power in watts
            # display some of the advanced field (just to test)
            # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
            print("Voltage (VIN+) : {:6.3f}   V".format(bus_voltage + shunt_voltage))
            print("Voltage (VIN-) : {:6.3f}   V".format(bus_voltage))
            print("Shunt Voltage  : {:8.5f} V".format(shunt_voltage))
            print("Shunt Current  : {:7.4f}  A".format(current / 1000))
            print("Power Calc.    : {:8.5f} W".format(bus_voltage * (current / 1000)))
            print("Power Register : {:6.3f}   W".format(power))
            print("")
                
    except Exception as e:
        print(f"An error occurred: {e}")
