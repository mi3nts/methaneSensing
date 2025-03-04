#!/bin/bash
#
# sleep 1
# echo "IPS7100"
# echo $(pgrep -f 'ips7100ReaderV1.py')
# sleep 2

sleep 1
echo "Air Mar"
echo $(pgrep -f 'airMarReader.py')
sleep 2

sleep 1
echo "Gasera One"
echo $(pgrep -f 'gaseraOneReader.py')
sleep 2

sleep 1
echo "INIR2ME5"
echo $(pgrep -f 'inir2me5Reader.py')
sleep 2

sleep 1
echo "SJH5"
echo $(pgrep -f 'sjh5Reader.py')
sleep 1

sleep 1
echo "TGS2611C00"
echo $(pgrep -f 'tgs2611c00Reader.py')
sleep 1

python3 ipReader.py
sleep 1