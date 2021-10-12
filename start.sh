#!/bin/bash

echo 'アプリを起動しています(7秒ほどかかります)'
sleep 7
cd "/home/pi/taskal-timecard-thermometer"
sudo python3 "/home/pi/taskal-timecard-thermometer/main.py"