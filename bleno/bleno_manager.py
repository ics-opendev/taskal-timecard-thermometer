from pybleno import *
import sys
import signal
from bleno.echo_characteristic import EchoCharacteristic

class BlenoManager:

    def __init__(self, environment):
        self.inner_bleno = Bleno()
        self.environment = environment
        self.inner_bleno.on('stateChange', self.onStateChange)
        self.inner_bleno.on('advertisingStart', self.onAdvertisingStart)

    def start(self):
        print('start bleno')
        self.inner_bleno.start()
    
    def stop(self):
        print('stop bleno')
        self.inner_bleno.stopAdvertising()
        self.inner_bleno.disconnect()

    def onStateChange(self, state):
        print('on -> stateChange: ' + state);

        if (state == 'poweredOn'):
            self.inner_bleno.startAdvertising('thermometer', ['ec00'])
        else:
            self.inner_bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: ' + ('error ' + error if error else 'success'));

        if not error:
            self.inner_bleno.setServices([
                BlenoPrimaryService({
                    'uuid': 'ec00',
                    'characteristics': [ 
                        EchoCharacteristic('thermometer')
                        ]
                })
            ])

