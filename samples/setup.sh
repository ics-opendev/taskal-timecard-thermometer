#!/bin/bash

set -e

# for OpenCV
pip3 install "numpy>=1.19.5" "opencv_python>=4.1,<5.0"

# for BodyTemp
pip3 install distro PyTurboJPEG
pip3 install "Kivy>=1.11,<2.0"
pip3 install "Flask>=1.1,<1.2"
