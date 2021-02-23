import argparse
import cv2
import os
import sys
import time
from owlifttypeh import OwhDevice, OwhMeta

ap = argparse.ArgumentParser()
ap.add_argument("-f0", "--file0", default = "cam0.owi", type = str)
ap.add_argument("-f1", "--file1", default = "cam1.owi", type = str)
ap.add_argument("-d", "--dir", default = None, type = str)
ap.add_argument("-m", "--manu_corr", default = 3.5, type = float)
ap.add_argument("-i", "--interval", default = 0, type = float)
ap.add_argument("-s", "--skip", default = 0, type = int)
args = ap.parse_args()

if args.dir:
    file0 = os.path.join(args.dir, args.file0)
    file1 = os.path.join(args.dir, args.file1)
else:
    file0 = args.file0
    file1 = args.file1

ow = OwhDevice.open(file0, file1)
wx, wy = ow.frame_size
ow.set_options({"manu_corr": args.manu_corr})

winName = 'Thermography'
text_offset = (2, 118)
text_color = (255, 255, 255)
cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
cv2.resizeWindow(winName, wx * 4, wy * 4)
skip_ms = args.skip * 1000

ow.capture_start()

while ow.alive:
    c = cv2.waitKey(1)
    if c == 27:
        break

    img, meta = ow.get_frame()

    if meta.file_time_ofs > skip_ms:
        aimg = ow.image_to_array(img)
        if meta.event_type == OwhMeta.EV_BODY_TEMP:
            cv2.putText(aimg, "{:.1f}".format(meta.body_temp),
                text_offset, cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 1, -1)
        cv2.imshow(winName, aimg)
        time.sleep(args.interval)
