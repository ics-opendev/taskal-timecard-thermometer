#!/bin/bash

sudo cp taskal-timecard-thermometer.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl status taskal-timecard-thermometer.service
sudo systemctl enable taskal-timecard-thermometer.service
sudo systemctl start taskal-timecard-thermometer.service

journalctl -u taskal-timecard-thermometer.service