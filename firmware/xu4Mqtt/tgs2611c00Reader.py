from ina219 import INA219
from ina219 import DeviceRangeError
import odroid_wiringpi as wpi
from pprint import pprint
from collections import OrderedDict
import datetime
wpi.wiringPiSetup()
import time
from mintsXU4 import mintsSensorReader as mSR
import sys

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.2

startTimePro = time.time()

loopInterval = 5 


try:
    ina   = INA219(SHUNT_OHMS, busnum=1)
    # print("Adafruit_GPIO.I2C" in str(inaSolarOut._i2c))
    ina.configure()

except Exception as e:
    time.sleep(.5)
    print ("Error and type: %s - %s." % (e,type(e)))
    time.sleep(.5)
    print("Methane Sensor not found")
    
    time.sleep(.5)
    sys.exit()

def read(startTimePro):
    startTime = startTimePro
    while True:
        try:
            dateTime = datetime.datetime.now()
            print(ina.power())
            print(ina.shunt_voltage())
            print(ina.current())
            sensorDictionary = OrderedDict([
                ("dateTime", str(dateTime)),
                ("methaneEQBusVoltage", ina.voltage()),  
                ("methaneEQCurrent"   , ina.power()),  
                        ])
            pprint(sensorDictionary)  
            print()                                 
            if time.time() - startTimePro> 60 :
                print("Sensor Warmed Up")
                mSR.sensorFinisher(dateTime,"TGS2611C00",sensorDictionary)

            startTime = mSR.delayMints(time.time() - startTime,loopInterval)


        except Exception as e:
            time.sleep(.5)
            print ("Error and type: %s - %s." % (e,type(e)))
            time.sleep(.5)
            print("Data Packet Not Sent for Methane")
            time.sleep(.5)


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    read(startTimePro)