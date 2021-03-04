#!/bin/bash

set -e

sudo apt update

sudo apt upgrade -y

sudo apt install -y libatlas3-base

sudo pip3 install owlifttypeh-1.0.0-py3-none-linux_armv7l.whl

sudo apt install -y libsdl2-ttf-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0

# bluetooth
sudo apt install -y bluetooth bluez libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev libdbus-glib-1-dev libbluetooth-dev

sudo chmod 777 samples/*

# install dependency
sudo pip3 install "distro" "PyTurboJPEG"
sudo pip3 install "numpy>=1.19.5" "opencv_python>=4.1,<5.0"
sudo pip3 install "Kivy>=1.11,<2.0"
sudo pip3 install "Pillow"
sudo pip3 install "requests"
sudo pip3 install "schedule"

# bluetooth LE peripheral (python)
sudo pip3 install "pybleno"