#!/bin/bash
#
sleep 1

kill $(pgrep -f 'airMarReader.py')
sleep 1

kill $(pgrep -f 'inir2me5Reader.py')
sleep 1

kill $(pgrep -f 'tgs2611c00Reader.py')
sleep 1


python3 ipReader.py
sleep 5