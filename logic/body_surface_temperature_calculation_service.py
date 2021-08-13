# coding: UTF-8
from owlifttypeh import OwhMeta
from owlifth.util import get_event_type
from entity.enum.measurement_type import MeasurementType
from entity.body_surface_temperature import BodySurfaceTemperature

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
        if meta.status is not OwhMeta.S_OK:
            return

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
            if get_event_type(meta) is OwhMeta.EV_DIST_VALID:
                self.human_detected = True
                self.human_detection_range = True
            if get_event_type(meta) is OwhMeta.EV_DIST_INVALID:
                self.human_detection_range = False
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
            return BodySurfaceTemperature(measurement_type, body_temp) 

        # システム側で温度を演算
        if self.human_detection_range:
            pass

        return BodySurfaceTemperature(measurement_type, body_temp)