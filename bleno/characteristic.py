from pybleno import *
import array
import struct
import sys
import traceback
import time
import datetime
from entity.body_surface_temperature import BodySurfaceTemperature
from entity.enum.measurement_type import MeasurementType

# 体温が検出できたことを管理する
class BodyTempCharacteristic(Characteristic):
    
    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read', 'notify', 'write'],
            'value': None
          })
        self._updateValueCallback = None
        self.current_body_temp = None
        self.activateNotification = False

    # リクエストの瞬間に適切な品質が得られているか検査し、得られない場合はnotifyを起動
    def onReadRequest(self, offset, callback):
        now_current_body_temp = self.current_body_temp

        if now_current_body_temp is None:
            time_out = bytes(f'-1', encoding='utf-8', errors='replace')
            callback(Characteristic.RESULT_SUCCESS, time_out[offset:])
            # notification を有効化
            self.activateNotification = True
            return

        callback(Characteristic.RESULT_SUCCESS, bytes(f'{now_current_body_temp.temperature}', encoding='utf-8', errors='replace'))
        print('read', now_current_body_temp.temperature)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        #48=人検出
        value = readUInt8(data, 0)
        if value == 48:
            self.current_body_temp = None
            self.activateNotification = False

        callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('onSubscribe:BodyTemp')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('onUnsubscribe:BodyTemp');
        
        self._updateValueCallback = None

    # 良い値がこれば、通知する、来ない場合は2秒待ち、高温ランダムを返す
    def updateBodyTemp(self, body_temp):
        new_body_temp = self.best_body_temp(self.current_body_temp, body_temp)

        value = bytes(f'-1', encoding='utf-8', errors='replace')
        if new_body_temp is not self.current_body_temp and new_body_temp is not None:
            self.current_body_temp = new_body_temp
            value = bytes(f'{self.current_body_temp.temperature}', encoding='utf-8', errors='replace')
            if self._updateValueCallback:
                self._updateValueCallback(value)
                print('notifiy', self.current_body_temp.temperature)
    
    def best_body_temp(self, a, b):
        if a is None:
            return b
        
        if self.is_expiration(a):
            return b
        
        if b is None:
            return None
        
        # 優先度チェック
        if a.measurement_type.value > b.measurement_type.value:
            return b
        else:
            return a
        
    def is_expiration(self, a):
        t = time.time() - a.created_at
        return t > 1.09


# サーモカメラのステータスを管理する
class ThermometerStatusCharacteristic(Characteristic):
    
    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read', 'notify'],
            'value': None
          })
          
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None

    def onReadRequest(self, offset, callback):
        callback(Characteristic.RESULT_SUCCESS, self._value[offset:])

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('onSubscribe:ThermometerStatus')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('onUnsubscribe:ThermometerStatus');
        
        self._updateValueCallback = None

    # 体温計が温度を取得した際はここが更新される
    def updateStatus(self, status_code):
        self._value = bytes(f'{status_code.value}', encoding='utf-8', errors='replace')

        if self._updateValueCallback:
            self._updateValueCallback(self._value)