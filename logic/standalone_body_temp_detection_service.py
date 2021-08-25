# coding: UTF-8
from entity.standalone_info import StandaloneInfo
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
    
    # 体表温度の演算を行う（演算結果、UIの変更箇所)
    def execute(self, body_temp):
        # TODO: 表示は検出後0.7秒
        # TODO: 3秒同じ位置かつ、-1なら削除
        human_detection = (0 < body_temp.distance and body_temp.distance < 620)
        if human_detection:
            old_body_temp = self.standalone_current_body_temp
            new_body_temp = self.standalone_best_body_temp(self.standalone_current_body_temp, body_temp)
            self.standalone_current_body_temp = new_body_temp
            # 温度検出に失敗していたら終了
            if new_body_temp is None or new_body_temp.temperature == -1:
                return StandaloneInfo(False, -1)

            # 成功していたら未検出回数をリセット
            self.lost_count = 0
            return StandaloneInfo(True, self.standalone_current_body_temp.temperature)
        elif self.standalone_current_body_temp is not None:
            self.lost_count += 1
            if self.lost_count > 3:
                self.standalone_current_body_temp = None
                self.lost_count = 0
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