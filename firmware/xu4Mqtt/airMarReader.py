
import serial
import datetime
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
import time
import serial
from collections import OrderedDict

dataFolder    =  mD.dataFolder
airmarPort    =  mD.airmarPort[0]
print(airmarPort)

def main():

    ser = serial.Serial(
    port= airmarPort,\
    baudrate=4800,\
    parity  =serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

    lastHCHDT = time.time()
    lastWIMWV = time.time()
    lastGPGGA = time.time()
    lastGPVTG = time.time()
    lastGPZDA = time.time()
    lastWIMDA = time.time()
    lastYXXDR = time.time()

    delta  = .5
    print("connected to: " + ser.portstr)

    #this will store the line
    line = []
    while True:
        try:
            for c in ser.read():
                line.append(chr(c))
                if chr(c) == '\n':
                    dataString     = (''.join(line)).replace("\r\n","")
                    dateTime  = datetime.datetime.now()
                    print(dataString)

                    if (dataString.startswith("$HCHDT") and mSR.getDeltaTimeAM(lastHCHDT,delta)):
                        mSR.HCHDTWriteAM(dataString,dateTime)
                        lastHCHDT = time.time()
                    # print(str(dataString))

                    if (dataString.startswith("$WIMWV") and mSR.getDeltaTimeAM(lastWIMWV,delta)):
                        mSR.WIMWVWriteAM(dataString,dateTime)
                        lastWIMWV = time.time()
                    # print(str(dataString))

                    if (dataString.startswith("$GPGGA") and mSR.getDeltaTimeAM(lastGPGGA,delta)):
                        mSR.GPGGAWriteAM(dataString,dateTime)
                        lastGPGGA = time.time()
                    # print(str(dataString))

                    if (dataString.startswith("$GPVTG") and mSR.getDeltaTimeAM(lastGPVTG,delta)):
                        mSR.GPVTGWriteAM(dataString,dateTime)
                        lastGPVTG = time.time()
                    # print(str(dataString))

                    if (dataString.startswith("$GPZDA") and mSR.getDeltaTimeAM(lastGPZDA,delta)):
                        mSR.GPZDAWriteAM(dataString,dateTime)
                        lastGPZDA = time.time()
                    # print(str(dataString))

                    if (dataString.startswith("$WIMDA") and mSR.getDeltaTimeAM(lastWIMDA,delta)):
                        mSR.WIMDAWriteAM(dataString,dateTime)
                        lastWIMDA = time.time()
                    # print(str(dataString))
            
                    
                    if (dataString.startswith("$YXXDR,A") and mSR.getDeltaTimeAM(lastYXXDR,delta)):
                        mSR.YXXDRWriteAM2(dataString,dateTime)
                        lastYXXDR = time.time()
                    # print(str(dataString))

                    line = []
                    break
        except:
            print("Incomplete String Read")
            line = []
                    
    ser.close()



if __name__ == "__main__":
   main()

