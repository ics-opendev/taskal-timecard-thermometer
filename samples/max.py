import numpy as np
import time
from owlifttypeh import OwhDevice

ow = OwhDevice.connect()
ow.set_options({ "image_tab": False,
        "temp_tab": True })
ow.capture_start()
fc0 = 0

while ow.alive:
    fc = ow.frame_counter
    if fc0 and fc == fc0:
        time.sleep(0.01)
        continue
    fc0 = fc
    img, meta = ow.get_frame()
    if meta.temp_tab is None:
        continue
    max_temp = np.max(meta.temp_tab)
    print("{:.2f}".format(max_temp - 273.15))
