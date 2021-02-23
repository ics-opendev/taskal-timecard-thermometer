import argparse
import cv2
from datetime import datetime
import numpy as np
import os
import re
from owlifttypeh import OwhDevice

K0 = 273.15

def get_region(region_path):
    if re.match(r'[0-9,]+', region_path):
        return list(map(lambda x: int(x), region_path.split(",")))

    with open(region_path, "r") as f:
        region_str = f.read()
    return list(map(lambda x: int(x), region_str.split(",")))


ap = argparse.ArgumentParser(add_help = False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("-h", "--help", action = 'help',
        help = 'このメッセージを表示する。画面表示の説明: 左下=放射率適用後の平均温度, 左上=放射率適用前の平均温度, 右下=30フレームごとの放射率適用後の最大温度, 右上=30フレームごとの放射率適用前の最大温度')
ap.add_argument("-e", "--emiss", default = 0.98, type = float,
        help = '放射率')
ap.add_argument("-s", "--target_dist", default = 900, type = int,
        help = '測定対象までの距離(mm)')
ap.add_argument("-r", "--region", default = "58,58,62,62", type = str,
        help = '"x1,y1,x2,y2"で指定する測定範囲。 各値は0～120。 x1 <= x < x2, y1 <= y < y2 が対象。')
ap.add_argument("-p", "--print", action = "store_const", dest = "print",
        const = True, default = False,
        help = '標準出力へ温度を出力する。 出力内容は [時刻], [左下の数値], [左上の数値], [右下の数値], [右上の数値]')
ap.add_argument("-f0", "--file0", default = None, type = str,
        help = 'カメラ0のowiファイルのパス')
ap.add_argument("-f1", "--file1", default = None, type = str,
        help = 'カメラ1のowiファイルのパス')
ap.add_argument("-d", "--dir", default = None, type = str,
        help = 'cam0.owi, cam1.owi が存在するディレクトリのパス')
ap.add_argument("-i", "--interval", default = 0.115, type = float,
        help = 'owiファイル再生時のインターバル(秒)')
args = ap.parse_args()

if args.dir:
    ow = OwhDevice.open(os.path.join(args.dir, "cam0.owi"),
            os.path.join(args.dir, "cam1.owi"))
elif args.file0:
    ow = OwhDevice.open(args.file0, args.file1)
else:
    ow = OwhDevice.connect()
wx, wy = ow.frame_size
ow.set_options({
    "temp_tab": True,
    "face_detect": False,
    "hide_bg": False,
    "target_emiss": args.emiss,
    "target_dist": args.target_dist,
    "use_dist": 2,
})

winName = 'Thermography'
text_offset1 = (2, 118)
text_offset2 = (2, 98)
text_offset3 = (64, 118)
text_offset4 = (64, 98)
text_color1 = (255, 255, 255)
text_color2 = (128, 128, 255)
text_color3 = (128, 255, 255)
text_color4 = (128, 255, 0)
cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
cv2.resizeWindow(winName, wx * 4, wy * 4)
# temp_tab には放射率が適用されている。
# 適用前の値を逆算するために e4 を用いる。
e4 = pow(args.emiss, 0.25)

ow.capture_start()
fc0 = 0
eid0 = 0
max_cnt = 0
max1 = 0
intvl = int(args.interval * 1000)
x1, y1, x2, y2 = get_region(args.region)

while ow.alive:
    c = cv2.waitKey(intvl)
    if c == 27:
        break

    fc = ow.frame_counter
    if fc0 and fc == fc0:
        continue

    fc0 = fc
    img, meta = ow.get_frame()
    aimg = ow.image_to_array(img)
    aimg = cv2.rectangle(aimg, (x1, y1), (x2 - 1, y2 - 1), (0, 0, 255), 1)

    if meta.temp_tab is not None:
        temp1 = np.mean(meta.temp_tab[x1:x2, y1:y2])
        temp2 = temp1 * e4
        temp1 -= K0
        temp2 -= K0
        max0 = np.max(meta.temp_tab[x1:x2, y1:y2])
        max_cnt += 1
        if max0 > max1:
            max1 = max0
            temp3 = max1 - K0
            temp4 = temp3 * e4
        if max_cnt == 30:
            if args.print:
                t = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                print("{},{:.2f},{:.2f},{:.2f},{:.2f}".format(t, temp1, temp2, temp3, temp4))
            max1 = 0
            max_cnt = 0
        cv2.putText(aimg, "{:.2f}".format(temp1),
            text_offset1, cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color1, 1, -1)
        cv2.putText(aimg, "{:.2f}".format(temp2),
            text_offset2, cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color2, 1, -1)
        cv2.putText(aimg, "{:.2f}".format(temp3),
            text_offset3, cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color3, 1, -1)
        cv2.putText(aimg, "{:.2f}".format(temp4),
            text_offset4, cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color4, 1, -1)

    cv2.imshow(winName, aimg)
