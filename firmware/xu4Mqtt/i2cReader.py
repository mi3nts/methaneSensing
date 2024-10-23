#!/usr/bin/python
# ***************************************************************************
#   I2CPythonMints
#   ---------------------------------
#   Written by: Lakitha Omal Harindha Wijeratne
#   - for -
#   MINTS :  Multi-scale Integrated Sensing and Simulation
#     & 
#   TRECIS: Texas Research and Education Cyberinfrastructure Services
#
#   ---------------------------------
#   Date: July 7th, 2022
#   ---------------------------------
#   This module is written for generic implimentation of MINTS projects
#   --------------------------------------------------------------------------
#   https://github.com/mi3nts
#   https://trecis.cyberinfrastructure.org/
#   http://utdmints.info/
#  ***************************************************************************



import sys
import time
import os
import smbus2
from i2cMints.i2c_scd30 import SCD30
from i2cMints.i2c_bme280 import BME280
from mintsXU4 import mintsSensorReader as mSR

debug  = False 

bus     = smbus2.SMBus(4)

scd30   = SCD30(bus,debug)
bme280  = BME280(bus,debug)
loopInterval = 5 


def main(loopInterval):
    scd30_valid    = scd30.initiate(30)
    bme280_valid   = bme280.initiate(30)
    startTime    = time.time()
    while True:
        try:
            print("======= BME280 ========")
            if bme280_valid:
                mSR.BME280WriteI2c(bme280.read())
            print("=======================")
            time.sleep(2)       
            print("======== SCD30 ========")
            if scd30_valid:
                mSR.SCD30WriteI2c(scd30.read())
            print("=======================")
            time.sleep(2)
            startTime = mSR.delayMints(time.time() - startTime,loopInterval)
            
        except Exception as e:
            print(e)
            time.sleep(10)
        
if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print("Monitoring Battery level for Mints Wearable Node")
    main(loopInterval)
