# coding: UTF-8
from entity.enum.measurement_type import MeasurementType
import time
import math

# 測定結果クラス
class BodySurfaceTemperature:
    # measurement_typeがNO_MEASUREMENTの場合はtemperatureが-1で固定される
    def __init__(self, measurement_type, temperature):
        # 測定方式
        self.measurement_type = measurement_type

        # 測定時刻
        self.created_at = time.time()
        
        # 測定温度
        if measurement_type == MeasurementType.NO_MEASUREMENT:
            self.temperature = -1
        else:
            self.temperature = math.floor(temperature * 10) / 10