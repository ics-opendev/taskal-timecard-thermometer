import argparse
import cv2
import numpy as np
from owlifttypeh import OwhDevice, OwhMeta

ap = argparse.ArgumentParser()
ap.add_argument("-m", "--max", action = "store_const", const = True,
        default = False, dest = "max")
ap.add_argument("-n", "--manu_corr", default = 3.5, type = float)
ap.add_argument("-c", "--correct-mode", default = 0, type = int)
ap.add_argument("-b", "--body-temp", default = 36.5, type = int)
args = ap.parse_args()

ow = OwhDevice.connect()
wx, wy = ow.frame_size
ow.set_options({
    "temp_tab": True,
    "manu_corr": args.manu_corr,
    "manual_body_temp": args.body_temp,
    "correct_mode": args.correct_mode,
})

winName = 'Thermography'
text_offset = (2, 118)
text_offset2 = (2, 20)
text_color = (255, 255, 255)
cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
cv2.resizeWindow(winName, wx * 4, wy * 4)

ow.capture_start()
fc0 = 0
eid0 = 0
msg = None
msg2 = None

while ow.alive:
    c = cv2.waitKey(1)
    if c == 27:
        break

    fc = ow.frame_counter
    if fc == fc0:
        continue

    fc0 = fc
    img, meta = ow.get_frame()

    if args.max and meta.temp_tab is not None:
        print("max={:.2f} stat={}  \r" \
                .format(np.max(meta.temp_tab) - 273.15, meta.status), end = '')

    eid = meta.event_id
    aimg = ow.image_to_array(img)

    if eid != eid0:
        if (meta.event_type & OwhMeta.EV_CORRECT) != 0:
            print("\ncorrect_cnt={:d} correct_error={:d}" \
                    .format(meta.correct_count, meta.correct_error))
        if (meta.event_type & OwhMeta.EV_BODY_TEMP) != 0:
            msg = "{:.2f}".format(meta.body_temp)
            msg2 = "({:d},{:d})".format(meta.body_temp_x, meta.body_temp_y)
        if (meta.event_type & OwhMeta.EV_LOST) != 0:
            msg = None
        if (meta.event_type & OwhMeta.EV_DIST_VALID) != 0:
            msg2 = "VALID"
        if (meta.event_type & OwhMeta.EV_DIST_INVALID) != 0:
            msg2 = "INVALID"
        eid0 = meta.event_id

    if msg:
        cv2.putText(aimg, msg,
            text_offset, cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 1, -1)
    if msg2:
        cv2.putText(aimg, msg2,
            text_offset2, cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 1, -1)
        msg2 = None

    cv2.imshow(winName, aimg)
