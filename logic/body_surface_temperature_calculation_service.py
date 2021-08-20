# coding: UTF-8
from owlifttypeh import OwhMeta
from owlifth.util import get_event_type
from entity.enum.measurement_type import MeasurementType
from entity.body_surface_temperature import BodySurfaceTemperature
import random
import math
import numpy as np

# 体温温度演算サービス
class BodySurfaceTemperatureCalculationService:
    def __init__(self):
        self.old_event_id = None
    
    # 体表温度の演算を行う（演算結果、UIの変更箇所)
    def execute(self, meta, manu_corr):
        if meta.status != OwhMeta.S_OK:
            return BodySurfaceTemperature(MeasurementType.NO_MEASUREMENT, -1, 0) 

        # 生の測定情報
        temp_table = meta.temp_tab

        # イベントを取得
        new_event_id = meta.event_id

        # 測定結果
        body_temp = -1
        measurement_type = MeasurementType.NO_MEASUREMENT
        
        # 測定距離
        distance = meta.distance

        # イベントに応じた処理
        if new_event_id is not self.old_event_id:
            if get_event_type(meta) is OwhMeta.EV_BODY_TEMP:
                body_temp = math.floor(meta.body_temp * 10) / 10
                measurement_type = MeasurementType.RAW_OWLIFT_H

        # 最後のイベント状況を保存
        self.old_event_id = new_event_id

        # サーモ側で測定できた場合は処理を終了
        if measurement_type is MeasurementType.RAW_OWLIFT_H:
            return BodySurfaceTemperature(measurement_type, body_temp, distance)

        # システム側で温度を演算        
        # 最大温度の取得
        max_temp = self.get_max_temp(temp_table) + manu_corr - 273.15
        range_result = self.range_check(max_temp)
        if range_result == 0:
            return BodySurfaceTemperature(MeasurementType.MAX_TEMPERATURE, max_temp, distance)

        # 範囲外（上限）の場合の演算を実施
        mean_temp = self.optimal_mean_temp(temp_table) + manu_corr - 273.15
        range_result = self.range_check(mean_temp)
        if range_result == 0:
            return BodySurfaceTemperature(MeasurementType.PERIPHERAL_TEMPERATURE, mean_temp, distance)
        
        # NOTE: 高温ばかりでるなら出現頻度から演算を実施を検討
        return BodySurfaceTemperature(MeasurementType.NO_MEASUREMENT, -1, distance)

    # 最大値の取得
    def get_max_temp(self, temp_table):
        return np.max(temp_table)
    
    # -1 なら範囲より小さい, 0なら範囲内, 1なら範囲より大きい
    def range_check(self, temp):
        if 35.85 > temp:
            return -1
        if 37.15 < temp:
            return 1

        return 0

    # 最小値のランダム生成    
    def min_random_value(self, temp):
        v = max(35.85, temp)
        return random.uniform(0, 0.25) + v

    # 周囲5px(中心と上下左右)の平均値
    def optimal_mean_temp(self, temp_table):
        flatten_temps = temp_table.flatten()
        sorted_indices = flatten_temps.argsort()[::-1]

        temps = []
        for index in sorted_indices[:10]:
            temp = self.get_mean_temp(index, flatten_temps)
            temps.append(temp)

        for temp in temps:
            if self.range_check(temp) == 0:
                return temp

        return sum(temps)/len(temps)
        

    def get_mean_temp(self, target_index, flatten_temps):
                # 中央
        count = 0
        sum_temp = 0
        sum_temp += flatten_temps[target_index]
        count += 1
        # 左
        if 0 <= (target_index-1) < len(flatten_temps):
            sum_temp += flatten_temps[target_index-1]
            count += 1
        # 右
        if 0 <= (target_index+1) < len(flatten_temps):
            sum_temp += flatten_temps[target_index+1]
            count += 1
        # 上
        if 0 <= (target_index-120) < len(flatten_temps):
            sum_temp += flatten_temps[target_index-120]
            count += 1
        # 下
        if 0 <= (target_index+120) < len(flatten_temps):
            sum_temp += flatten_temps[target_index+120]
            count += 1
        
        return sum_temp/count