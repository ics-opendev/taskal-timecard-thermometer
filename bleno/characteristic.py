from pybleno import Characteristic
import array
import struct
import sys
import traceback

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
        print('onSubscribe')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('onUnsubscribe');
        
        self._updateValueCallback = None

    # 体温計が温度を取得した際はここが更新される
    def updateBodyTemp(self, measured_temperature, measured_distance):
        self._value = f'{measured_temperature} {measured_distance}'

        if self._updateValueCallback:
            print('onWriteRequest: notifying'); 
            self._updateValueCallback(self._value)
