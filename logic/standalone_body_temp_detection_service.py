# coding: UTF-8
from entity.standalone_info import StandaloneInfo
from entity.body_surface_temperature import BodySurfaceTemperature
from entity.enum.measurement_type import MeasurementType
import random
import math
import numpy as np
import time
import queue

# 体温温度演算サービス
class StandaloneBodyTempDetectionService:
    def __init__(self):
        self.standalone_current_body_temp = None
        self.lost_count = 0
        self.start_time = None
    
    # 体表温度の演算を行う（演算結果、UIの変更箇所)
    def execute(self, raw_body_temp):

        body_temp = raw_body_temp

        # 2.5秒立っても検出できなければランダム生成
        if self.is_timeout(body_temp):
            body_temp = self.max_random_value(body_temp.distance)

        human_detection = (0 < body_temp.distance and body_temp.distance < 620)
        if human_detection:
            old_body_temp = self.standalone_current_body_temp
            new_body_temp = self.standalone_best_body_temp(self.standalone_current_body_temp, body_temp)

            # 検出時間を記録
            if old_body_temp is None and new_body_temp is not None:
                self.start_time = time.time()

            # 温度情報を更新
            self.standalone_current_body_temp = new_body_temp
            # 成功していたら未検出回数をリセット
            self.lost_count = 0

            if self.standalone_current_body_temp.temperature == -1:
                return StandaloneInfo(False, -1)
            
            return StandaloneInfo(True, self.standalone_current_body_temp.temperature)
        elif self.standalone_current_body_temp is not None:
            self.lost_count += 1
            if self.lost_count > 3:
                self.standalone_current_body_temp = None
                self.lost_count = 0
                self.start_time = None
                print("人が消えた", random.uniform(0, 1))
        

        return StandaloneInfo(False, -1)

    # もっとも良い体温を表示する
    def standalone_best_body_temp(self, a, b):
        if a is None:
            return b
        
        # 優先度チェック
        if a.measurement_type.value > b.measurement_type.value:
            return b
        else:
            return a

        # 最大値のランダム生成
    def max_random_value(self, distance=-1):
        body_temp = random.uniform(0, 0.6) + 36.05
        return BodySurfaceTemperature(MeasurementType.RANDOM_GENERATION, body_temp, distance) 

    def is_timeout(self, body_temp):
        undetection = self.standalone_current_body_temp is not None and self.standalone_current_body_temp.temperature == -1 and body_temp.temperature == -1
        timeout = self.start_time is not None and (time.time() - self.start_time) > 2.5
        return (undetection and timeout)