# coding: utf-8
from enum import Enum
import threading

from owlifttypeh import OwhMeta

# enumの速度が遅いとの情報があるため、処理速度が遅い場合は要確認
# 測定端末の状態(sails-ttcと共通)
class ThermoStatus(Enum):
    # 0:カメラ準備中
    PREPARATION = 0
    # 1:動作中
    OK = 1
    # 99:エラー
    ERROR = 99

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

    