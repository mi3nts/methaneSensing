import time
import datetime

import adafruit_gps
from adafruit_extended_bus import ExtendedI2C as I2C

from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD




def main():


    delta  = .5
    lastGPRMC = time.time()
    lastGPGGA = time.time()

    try:  
    # Detecting if the GPS is Connected
        i2c = I2C(4)
        gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False) # Use I2C interface
        print("GPS found")
    except Exception as e:
        time.sleep(.5)
        print("No GPS found")
        print ("Error and type: %s - %s." % (e,type(e)))
        quit()

    # Turn on everything (not all of it is parsed!)
    print("Sending GPS Command")
    gps.send_command(b"PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0")

    print("Changing Update Frequency")
    #gps.send_command(b"PMTK220,1000")


    while True:
        try:  
            if not gps.update() or not gps.has_fix:
                time.sleep(0.01)
                print("No Coordinates found")
                print(gps.nmea_sentence) 
                continue
            dateTime  = datetime.datetime.now()
            dataString = gps.nmea_sentence
            if (dataString.startswith("$GPGGA") or dataString.startswith("$GNGGA")) and mSR.getDeltaTime(lastGPGGA,delta):
                mSR.GPSGPGGA2Write(dataString,dateTime)
                lastGPGGA = time.time()
            if (dataString.startswith("$GPRMC") or dataString.startswith("$GNRMC")) and mSR.getDeltaTime(lastGPRMC,delta):
                mSR.GPSGPRMC2Write(dataString,dateTime)
                lastGPRMC = time.time()
        except Exception as e:
            time.sleep(.5)
            print("GPS Error")
            print ("Error and type: %s - %s." % (e,type(e)))

if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print("Monitoring GPS Sensor via i2c")
    main()