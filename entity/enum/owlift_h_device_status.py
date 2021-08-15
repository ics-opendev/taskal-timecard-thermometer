# coding: UTF-8
from enum import Enum


# ソフトウェアからみたデバイスのステータス
class OwliftHDeviceStatus(Enum):
    # 準備完了
    READY = 0
    # 準備中
    PREPARATION = 1
    # サーモとの接続が切れました
    THERMO_LOST = 99
    # 切断
    DISSCONNECTE = 100