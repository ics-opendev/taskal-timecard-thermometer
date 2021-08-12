# coding: UTF-8
from entity.enum.owlift_h_device_status import OwliftHDeviceStatus

# owlift_hのステータスを記録したクラス
class OwliftHStatus:
    def __init__(self):
        # サーモの初期校正が完了したかを保持
        self.preparation = False
        # 現在のデバイスステータス
        self.current_status = OwliftHDeviceStatus.DISSCONNECTE