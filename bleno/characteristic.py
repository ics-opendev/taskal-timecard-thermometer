from pybleno import *
import array
import struct
import sys
import traceback
import time

# 体温が検出できたことを管理する
class BodyTempCharacteristic(Characteristic):
    
    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read', 'notify'],
            'value': None
          })
          
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
        self.latestUpdateTime = time.time()

    def onReadRequest(self, offset, callback):
        if (time.time() - self.latestUpdateTime) > 0.7:
            time_out = bytes(f'-1 -1', encoding='utf-8', errors='replace')
            callback(Characteristic.RESULT_SUCCESS, time_out[offset:])

        callback(Characteristic.RESULT_SUCCESS, self._value[offset:])

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('onSubscribe:BodyTemp')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('onUnsubscribe:BodyTemp');
        
        self._updateValueCallback = None

    # 体温計が温度を取得した際はここが更新される
    def updateBodyTemp(self, measured_temperature, measured_distance):
        self.latestUpdateTime = time.time()
        self._value = bytes(f'{measured_temperature} {measured_distance}', encoding='utf-8', errors='replace')

        if self._updateValueCallback:
            print('updateBodyTemp: notifying'); 
            self._updateValueCallback(self._value)

# 人の検出や見失いを管理する
class HumanDetectionCharacteristic(Characteristic):
    
    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['write'],
            'value': None
          })
        
        self.detected = False
        self._updateValueCallback = None

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        a = readUInt16BE(data, 0)
        print(a)

        callback(self.RESULT_SUCCESS)

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
        self._value = bytes(f'{status_code}', encoding='utf-8', errors='replace')

        if self._updateValueCallback:
            print('updateStatus: notifying'); 
            self._updateValueCallback(self._value)