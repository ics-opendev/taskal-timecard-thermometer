import cv2
from owlifttypeh import OwhDevice

ow = OwhDevice.connect()
wx, wy = ow.frame_size
ow.set_options({"hide_bg": False})

winName = 'Thermography'
cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
cv2.resizeWindow(winName, wx * 4, wy * 4)
ow.capture_start()
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
