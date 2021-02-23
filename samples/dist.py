import time
from owlifttypeh import OwhDevice

ow = OwhDevice.connect()
wx, wy = ow.frame_size
ow.set_options({"image_tab": False, "face_detect": False})

ow.capture_start()
fc0 = 0

while ow.alive:
    fc = ow.frame_counter
    if fc == fc0:
        time.sleep(0.01)
        continue

    fc0 = fc
    _, meta = ow.get_frame()
    print("distance = {:4d}".format(meta.distance))
