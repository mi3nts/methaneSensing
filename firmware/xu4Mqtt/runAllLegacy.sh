#!/bin/bash
#
sleep 6

#exec &> /home/teamlary/gitHubRepos/errorLogs/script_log.txt
#> out.txt 2> err.txt


if pgrep -f "ips7100ReaderV1.py" >/dev/null; then
    echo " ips7100ReaderV1.py already running."
else
    echo "ips7100ReaderV1.py not running. Starting it again..."
    python3 ips7100ReaderV1.py > /home/teamlary/gitHubRepos/errorLogs/ips7100ReaderV1.log 2> /home/teamlary/gitHubRepos/errorLogs/ips7100ReaderV1Err.log &
fi
sleep 5


if pgrep -f "i2cReader.py" >/dev/null; then
    echo " i2cReader.py already running."
else
    echo "i2cReader.py not running. Starting it again..."
    python3 i2cReader.py > /home/teamlary/gitHubRepos/errorLogs/i2cReader.log 2> /home/teamlary/gitHubRepos/errorLogs/i2cReaderErr.log &
fi
sleep 5


if pgrep -f "gpsReader.py" >/dev/null; then
    echo " gpsReader.py already running."
else
    echo "gpsReader.py not running. Starting it again..."
    python3 gpsReader.py > /home/teamlary/gitHubRepos/errorLogs/gpsReader.log 2> /home/teamlary/gitHubRepos/errorLogs/gpsReaderErr.log &
fi
sleep 5

if pgrep -f "batteryReader.py" >/dev/null; then
    echo " batteryReader.py already running."
else
    echo "batteryReader.py not running. Starting it again..."
    python3 batteryReader.py > /home/teamlary/gitHubRepos/errorLogs/batteryReader.log 2> /home/teamlary/gitHubRepos/errorLogs/batteryReaderErr.log &
fi
sleep 5


if pgrep -f "ipReader.py" >/dev/null; then
    echo " ipReader.py already running."
else
    echo "ipReader.py not running. Starting it again..."
    python3 ipReader.py > /home/teamlary/gitHubRepos/errorLogs/ipReader.log 2> /home/teamlary/gitHubRepos/errorLogs/ipReaderErr.log &
fi
sleep 5