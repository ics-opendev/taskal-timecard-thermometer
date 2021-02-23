rem for OpenCV
rem Avoid the problem: https://developercommunity.visualstudio.com/content/problem/1207405/fmod-after-an-update-to-windows-2004-is-causing-a.html
pip3 install "numpy>=1.19.5" "opencv_python>=4.1,<5.0"

rem for BodyTemp
pip3 install distro PyTurboJPEG
pip3 install "Kivy>=1.11,<2.0" "pypiwin32>=223" "kivy_deps.angle>=0.2.0,<0.3" "kivy_deps.glew>=0.2,<0.3" "kivy_deps.sdl2>=0.2,<0.3"
pip3 install "Flask>=1.1,<1.2"
