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
          
    def onReadRequest(self, offset, callback):
        print('onReadRequest: value = %s' % ([hex(c) for c in self._value]))
        callback(Characteristic.RESULT_SUCCESS, self._value[offset:])

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data
        
        print(data)
        print(offset)

        print('onWriteRequest: value = %s' % ([hex(c) for c in self._value]))

        if self._updateValueCallback:
            print('onWriteRequest: notifying');
            
            self._updateValueCallback(self._value)
        
        callback(Characteristic.RESULT_SUCCESS)
        
    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('onSubscribe')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('onUnsubscribe');
        
        self._updateValueCallback = None