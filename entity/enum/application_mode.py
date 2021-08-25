# coding: UTF-8
from enum import Enum


# 体表温度の検出方法
class ApplicationMode(Enum):
    # 機器連携
    DEVICE_COLLABORATION = 0
    # 単体動作
    STANDALONE = 1