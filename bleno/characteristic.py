from pybleno import Characteristic
import array
import struct
import sys
import traceback

class BodyTempCharacteristic(Characteristic):
    
    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read', 'write', 'notify'],
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

    def onReadRequest(self, offset, callback):
        print('EchoCharacteristic - %s - onReadRequest: value = %s' % (self['uuid'], [hex(c) for c in self._value]))
        callback(Characteristic.RESULT_SUCCESS, self._value[offset:])

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data

        print(type(data))

        print('EchoCharacteristic - %s - onWriteRequest: value = %s' % (self['uuid'], [hex(c) for c in self._value]))

        if self._updateValueCallback:
            print('EchoCharacteristic - onWriteRequest: notifying');
            
            self._updateValueCallback(self._value)
        
        callback(Characteristic.RESULT_SUCCESS)

    # 体温計が温度を取得した際はここが更新される
    def updateBodyTemp(self, measured_temperature, measured_distance):
        self._value = f'{measured_temperature} {measured_distance}'

        if self._updateValueCallback:
            print('onWriteRequest: notifying'); 
            self._updateValueCallback(self._value)
