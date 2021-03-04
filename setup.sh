#!/bin/bash

set -e

sudo apt update

sudo apt upgrade -y

sudo apt install -y libatlas3-base

pip3 install owlifttypeh-1.0.0-py3-none-linux_armv7l.whl

sudo apt install -y libsdl2-ttf-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0

# bluetooth
sudo apt install -y bluetooth libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev libdbus-glib-1-dev libbluetooth-dev

sudo chmod 777 samples/*

# install dependency
pip3 install "distro" "PyTurboJPEG"
pip3 install "numpy>=1.19.5" "opencv_python>=4.1,<5.0"
pip3 install "Kivy>=1.11,<2.0"
pip3 install "Pillow"
pip3 install "requests"
pip3 install "schedule"

# bluetooth (python)
cd ..
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.56.tar.xz
xz -dv bluez-5.56.tar.xz
tar -xf bluez-5.56.tar
cd bluez-5.56/
./configure --enable-experimental
make -j4
sudo make install
sudo pip3 install pybluez
cd ..
cd taskal-timecard-thermometer
