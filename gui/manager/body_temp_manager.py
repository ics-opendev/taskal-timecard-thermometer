# coding: utf-8
import threading
from datetime import datetime
import copy
import math

from api.taskal_api_client import TaskalApiClient
from api.taskal_api_client import ThermoStatus
from owlifttypeh import OwhMeta

# サーバ送信1回分の測定値
class OneCycleBodyTempInfo:

    def __init__(self):
        # 送信するデータ
        self.measured_temperature = -1
        self.measured_distance = -1
        self.status = ThermoStatus.PREPARATION
        # 送信が必要かのフラグ
        self.body_temp_need_sending = False

    def __deepcopy__(self):
        deepcopy_obj = OneCycleBodyTempInfo()
        deepcopy_obj.measured_temperature = self.measured_temperature
        deepcopy_obj.measured_distance = self.measured_distance
        deepcopy_obj.status = self.status
        deepcopy_obj.body_temp_need_sending = self.body_temp_need_sending
        return deepcopy_obj

# 測定値を管理するクラス
class BodyTempManager:
    def __init__(self, environment):
        # APIクライアント
        self.api = TaskalApiClient(environment.BASE_URL, environment.SERVER_SUBSCRIPTION_KEY, environment.UUID)
        # マルチスレッド対策でロックを作成
        self.lock = threading.Lock()
        # 現在の体温状況
        self.current_body_temp = OneCycleBodyTempInfo()


    # 体温情報の更新
    def update_body_temp(self, meta, meta_status):
        # 値操作を行うためロックを実行
        self.lock.acquire()

        # 測定体温
        current_body_temp = math.floor(meta.body_temp * 10) / 10
        # 測定距離
        current_distance = meta.distance

        if meta_status == OwhMeta.EV_BODY_TEMP: # 発見した人の体温を測定成功
            self.current_body_temp.measured_temperature = current_body_temp
            self.current_body_temp.measured_distance = current_distance
            self.current_body_temp.status = ThermoStatus.OK 
            self.current_body_temp.body_temp_need_sending = True

        # 操作が完了したのでロックを解除
        self.lock.release()

    def try_send_current_body_temp(self):
        # 値操作を行うためロックを実行
        self.lock.acquire()

        if self.current_body_temp.body_temp_need_sending:
            self.api.post_thermometer_output(
                measuredTemperature=self.current_body_temp.measuredTemperature,
                measuredDistance=self.current_body_temp.measuredDistance,
                status=self.current_body_temp.status
                )
            # 送信後は新しいデータを追加
            self.current_body_temp = OneCycleBodyTempInfo()

        # 操作が完了したのでロックを解除
        self.lock.release()


    