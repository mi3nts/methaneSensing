
import socket
from datetime import datetime, timezone
import time 
import re
from collections import OrderedDict
import pprint
import sys 
from mintsXU4 import mintsSensorReader as mSR

from gaseraOne.gaseraOne import GaseraOneSensor

hostIP          = "192.168.20.119"

defaultTaskID   = "11"

if __name__ == "__main__":
    print("==========================================")
    print("================== MINTS =================")
    print("------------------------------------------")

    # Create an instance of the sensor
    sensor = GaseraOneSensor(hostIP,defaultTaskID)
    
    # STARTING SEQUENCE 
    if not sensor.connect():
        print("Failed to connect to sensor. Exiting...")
        sys.exit(1)  # Exit with an error code

    sensor.startUpSequece()



    while True:
        try:
            print(sensor.request_last_measurement_results())
            time.sleep(60)

            if (time.time() - sensor.periodicCheckTime) > 3600:
                sensor.periodicCheck()

            if (time.time() - sensor.periodicCheckTime) > 6086400:
                sensor.dailyCheck()

        except KeyboardInterrupt:
            print("\nUser interrupted. Exiting...")
            break  # Exit the loop graceful


        except Exception as e:
            time.sleep(60)
            print ("Error and type: %s - %s." % (e,type(e)))
            time.sleep(.5)
            print("Data Packet Not Sent for Gasera One")
            time.sleep(.5)


    time.sleep(10)
    print(sensor.stop_measurement())
    
    # Disconnect when done
    sensor.disconnect()

    print("==========================================")
    print("=============== MINTS DONE ===============")
    print("------------------------------------------")
