# coding: utf-8
import threading

from api.taskal_api_client import TaskalApiClient
from api.taskal_api_client import ThermoStatus
from owlifttypeh import OwhMeta

# 測定値(不変クラス)
class BodyTempInfo:

    def __init__(self, measuredTemperature=-1, measuredDistance=-1, status=ThermoStatus.PREPARATION):
        self.measuredTemperature = measuredTemperature
        self.measuredDistance = measuredDistance
        self.status = ThermoStatus.PREPARATION

# 測定値を管理するクラス
class BodyTempManager:
    def __init__(self, environment):
        # APIクライアント
        self.api = TaskalApiClient(environment.BASE_URL, environment.SERVER_SUBSCRIPTION_KEY, environment.UUID)
        # マルチスレッド対策でロックを作成
        self.lock = threading.Lock()
        # 取得した体温をサーバに送る形にする最小集計時間 1000ms
        self.totalizationMs = 1000
        # 計測体温
        self.measuredTemperature = -1
        # 計測距離
        self.measuredDistance = -1
        # カメラステータス
        self.status = ThermoStatus.PREPARATION
        # testcode
        self.count = 0

    # 体温情報の更新
    def update_body_temp(self, meta, meta_status):
        # 値操作を行うためロックを実行
        self.lock.acquire()

        self.count += 1

        # 操作が完了したのでロックを解除
        self.lock.release()

    def try_send_current_body_temp(self):
        # TESTCODE
        self.api.post_thermometer_output(measuredTemperature=self.count)

    