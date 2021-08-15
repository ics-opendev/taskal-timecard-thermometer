# coding: UTF-8
from enum import Enum


# 体表温度の検出方法
class MeasurementType(Enum):
    # 生の測定結果
    RAW_OWLIFT_H = 1
    # 最高温度を取得
    MAX_TEMPERATURE = 2
    # 周辺温度から取得
    PERIPHERAL_TEMPERATURE = 3
    # 出現頻度から取得
    APPEARANCE_FREQUENCY = 4
    # 乱数による生成
    RANDOM_GENERATION = 5
    # 測定なし
    NO_MEASUREMENT = 6