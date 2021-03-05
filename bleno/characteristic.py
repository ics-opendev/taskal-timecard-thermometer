from pybleno import Characteristic
import array
import struct
import sys
import traceback

# 体温が検出できたことを管理する
class BodyTempCharacteristic(Characteristic):
    
    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['notify'],
            'value': None
          })
          
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('onSubscribe:BodyTemp')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('onUnsubscribe:BodyTemp');
        
        self._updateValueCallback = None

    # 体温計が温度を取得した際はここが更新される
    def updateBodyTemp(self, measured_temperature, measured_distance):
        self._value = bytes(f'{measured_temperature} {measured_distance}', encoding='utf-8', errors='replace')

        if self._updateValueCallback:
            print('updateBodyTemp: notifying'); 
            self._updateValueCallback(self._value)

# 人の検出や見失いを管理する
class HumanDetectionCharacteristic(Characteristic):
    
    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['notify'],
            'value': None
          })
          
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('onSubscribe:HumanDetection')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('onUnsubscribe:HumanDetection');
        
        self._updateValueCallback = None

    # 人を検出した場合に通知する
    def updateHumanDetection(self, human_detection):
        self._value = bytes(human_detection, encoding='utf-8', errors='replace')

        if self._updateValueCallback:
            print('updateHumanDetection: notifying'); 
            self._updateValueCallback(self._value)

# サーモカメラのステータスを管理する
class ThermometerStatusCharacteristic(Characteristic):
    
    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['notify'],
            'value': None
          })
          
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('onSubscribe:ThermometerStatus')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('onUnsubscribe:ThermometerStatus');
        
        self._updateValueCallback = None

    # 体温計が温度を取得した際はここが更新される
    def updateStatus(self, status_code, message):
        self._value = bytes(f'{status_code} {message}', encoding='utf-8', errors='replace')

        if self._updateValueCallback:
            print('updateStatus: notifying'); 
            self._updateValueCallback(self._value)