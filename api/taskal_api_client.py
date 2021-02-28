# coding: utf-8
from enum import Enum
import requests
import json
import datetime
from concurrent.futures import ThreadPoolExecutor

# enumの速度が遅いとの情報があるため、処理速度が遅い場合は要確認
# 測定端末の状態(sails-ttcと共通)
class ThermoStatus(Enum):
    # 0:カメラ準備中
    PREPARATION = 0
    # 1:動作中
    OK = 1
    # 99:エラー
    ERROR = 99

class TaskalApiClient():
    
    def __init__(self, base_url, server_subscription_key, uuid):
        self.base_url = base_url
        self.server_subscription_key = server_subscription_key
        self.uuid = uuid
        # max_workersは基本的にpythonがCPUに基づいて計算するので、指定なしが無難
        # https://docs.python.org/ja/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
        self.tpe = ThreadPoolExecutor()

        # NOTE:  (connect timeout, read timeout)
        # 
        self.timeout = (15, 30)
    
    # サーモメータが検出した情報を送信
    def post_thermometer_output(self, measuredTemperature=-1, measuredDistance=-1, status=ThermoStatus.ERROR):
        try:
            dt_now = datetime.datetime.now()
            measured_at = dt_now.strftime('%Y-%m-%dT%H:%M:%S')

            request_url = f'{self.base_url}/api/v1/thermometeroutput'
            
            body = {
                'raspiDeviceId': self.uuid,
                'measuredAt': measured_at,
                'measuredTemperature': measuredTemperature,
                'measuredDistance': measuredDistance,
                'status': status.value,
                }
            body_json = json.dumps(body)

            headers = {
                    'Content-Type': 'application/json',
                    'Authorization': self.server_subscription_key
                    }

            # 並列実行
            # 同期的な下記コードと同一
            # requests.post(
            #    request_url,
            #    data=body_json,
            #    headers=headers,
            #    timeout=self.timeout
            #)
            self.tpe.submit(requests.post, request_url, data=body_json, headers=headers, timeout=self.timeout)
        except Exception:
            # TODO: ログの実装
            pass