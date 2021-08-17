# coding: UTF-8
from entity.enum.owlift_h_device_status import OwliftHDeviceStatus

# owlift_hのステータスを記録したクラス
class OwliftHStatus:
    def __init__(self, status):
        # 現在のデバイスステータス
        self.status = status