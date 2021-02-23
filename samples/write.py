import argparse
import cv2
import os
from owlifttypeh import OwhDevice

ap = argparse.ArgumentParser()
ap.add_argument("-f0", "--file0", default = "cam0.owi", type = str)
ap.add_argument("-f1", "--file1", default = "cam1.owi", type = str)
ap.add_argument("-d", "--dir", default = None, type = str)
ap.add_argument("-m", "--manu_corr", default = 3.5, type = float)
ap.add_argument("-b", "--show-bg", action = "store_const",
        dest = "hide_bg", const = False, default = True)
ap.add_argument("-F", "--disable-face-detect", action = "store_const",
        dest = "face_detect", const = False, default = True)
args = ap.parse_args()

if args.dir:
    file0 = os.path.join(args.dir, args.file0)
    file1 = os.path.join(args.dir, args.file1)
else:
    file0 = args.file0
    file1 = args.file1

ow = OwhDevice.connect()
wx, wy = ow.frame_size
ow.set_options({
    "manu_corr": args.manu_corr,
    "hide_bg": args.hide_bg,
    "face_detect": args.face_detect,
})

winName = 'Thermography'
cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
cv2.resizeWindow(winName, wx * 4, wy * 4)

ow.capture_start()
ow.write_start(file0, file1)
fc0 = 0

while ow.alive:
    c = cv2.waitKey(1)
    if c == 27:
        break
    fc = ow.frame_counter
    if fc == fc0:
        continue

    fc0 = fc
    img, meta = ow.get_frame()

    cv2.imshow(winName, ow.image_to_array(img))
