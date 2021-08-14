# coding: UTF-8
from owlifttypeh import OwhMeta
from owlifth.util import get_event_type
from entity.enum.measurement_type import MeasurementType
from entity.body_surface_temperature import BodySurfaceTemperature
import random
import math

# 体温温度演算サービス
class BodySurfaceTemperatureCalculationService:
    def __init__(self):
        self.old_event_id = None
        # 人検出
        self.human_detected = False
        # 測定範囲内
        self.human_detection_range = False
    
    # 体表温度の演算を行う（演算結果、UIの変更箇所)
    def execute(self, img, meta, manu_corr):
        if meta.status != OwhMeta.S_OK:
            print("ステータスがOKではない")
            return BodySurfaceTemperature(MeasurementType.NO_MEASUREMENT, -1) 

        # 生の測定情報
        temp_table = meta.temp_tab

        # イベントを取得
        new_event_id = meta.event_id

        # 測定結果
        body_temp = -1
        measurement_type = MeasurementType.NO_MEASUREMENT
        
        # イベントに応じた処理
        if new_event_id is not self.old_event_id:
            if get_event_type(meta) is OwhMeta.EV_LOST:
                self.human_detected = False
                print("人を見失いました")
            if get_event_type(meta) is OwhMeta.EV_DIST_VALID:
                self.human_detected = True
                self.human_detection_range = True
                print("人を検出しました")
            if get_event_type(meta) is OwhMeta.EV_DIST_INVALID:
                self.human_detection_range = False
                print("人が測定範囲外に出ました")
            if get_event_type(meta) is OwhMeta.EV_BODY_TEMP:
                body_temp = math.floor(meta.body_temp * 10) / 10
                measurement_type = MeasurementType.RAW_OWLIFT_H

        # 最後のイベント状況を保存
        self.old_event_id = new_event_id

        # サーモ側で測定できた場合は処理を終了
        if measurement_type is MeasurementType.RAW_OWLIFT_H:
            return BodySurfaceTemperature(measurement_type, body_temp)

        # 人検出事体が行われていない場合
        if not self.human_detected:
            print("人がおらんです")
            return BodySurfaceTemperature(measurement_type, body_temp) 

        # システム側で温度を演算
        
        # 最大温度の取得
        max_temp = self.get_max_temp(temp_table) + manu_corr
        range_result = self.range_check(max_temp)
        if range_result == 0:
            return BodySurfaceTemperature(MeasurementType.MAX_TEMPERATURE, max_temp)
        elif range_result == -1:
            min_value = self.min_random_value(max_temp)
            return BodySurfaceTemperature(MeasurementType.RANDOM_GENERATION, min_value)

        # 範囲外（上限）の場合の演算を実施
        mean_temp = mean_max_temp() + manu_corr
        range_result = self.range_check(mean_temp)
        if range_result == 0:
            return BodySurfaceTemperature(MeasurementType.PERIPHERAL_TEMPERATURE, mean_temp)
        
        # NOTE: 高温ばかりでるなら出現頻度から演算を実施を検討

        # 高温用乱数で演算を実施
        body_temp = max_random_value(max_temp)
        measurement_type = MeasurementType.RANDOM_GENERATION

        return BodySurfaceTemperature(measurement_type, body_temp)

    # 最大値の取得
    def get_max_temp(self, temp_table):
        return np.max(meta.temp_tab)
    
    # -1 なら範囲より小さい, 0なら範囲内, 1なら範囲より大きい
    def range_check(self, temp):
        if 35.9 > temp:
            return -1
        if 37.1 < temp:
            return 1

        return 0

    # 最小値のランダム生成    
    def min_random_value(self, temp):
        r = 35.9 - max(35.7, temp)
        return random.uniform(0, r) + temp
    
    # 最大値のランダム生成
    def max_random_value(self, temp):
        r = 37.2 - min(37.6, temp)
        return random.uniform(0, r) + 36.7  

    # 周囲5px(中心と上下左右)の平均値
    def mean_max_temp(self, temp_table):
        flatten_temps = temp_table.flatten()
        max_index = np.argmax(flatten_temps)
        # 中央
        count = 0
        sum_temp = 0
        sum_temp += flatten_temps[max_index]
        count += 1
        # 左
        if 0 < (max_index) <= len(flatten_temps):
            sum_temp += flatten_temps[max_index-1]
            count += 1
        # 右
        if 0 < (max_index+1) <= len(flatten_temps):
            sum_temp += flatten_temps[max_index+1]
            count += 1
        # 上
        if 0 < (max_index-120) <= len(flatten_temps):
            sum_temp += flatten_temps[max_index-120]
            count += 1
        # 下
        if 0 < (max_index+120) <= len(flatten_temps):
            sum_temp += flatten_temps[max_index+120]
            count += 1
        
        return sum_temp/count