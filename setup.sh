#!/bin/bash

set -e

# うまく動かない時
# https://kaworu.jpn.org/ubuntu/apt_update%E3%81%8C%E3%82%A4%E3%83%B3%E3%83%87%E3%83%83%E3%82%AF%E3%82%B9%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%AE%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89%E3%81%AB%E5%A4%B1%E6%95%97%E3%81%99%E3%82%8B%E5%A0%B4%E5%90%88%E3%81%AE%E5%AF%BE%E5%87%A6%E6%B3%95
sudo apt update

sudo apt upgrade -y

sudo apt install -y libatlas3-base

sudo pip3 install owlifttypeh-1.0.1-py3-none-linux_armv7l.whl

sudo apt install -y libsdl2-ttf-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0

# bluetooth
sudo apt install -y bluetooth bluez libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev libdbus-glib-1-dev libbluetooth-dev

# install dependency
sudo pip3 install "distro" "PyTurboJPEG"
sudo pip3 install "numpy>=1.19.5" "opencv_python>=4.1,<5.0"
sudo pip3 install "Kivy>=1.11,<2.0"
sudo pip3 install "Pillow"
sudo pip3 install "requests"
sudo pip3 install "schedule"

# bluetooth LE peripheral (python)
sudo pip3 install "pybleno"
