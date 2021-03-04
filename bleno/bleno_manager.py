from pybleno import *
import sys
import signal
from bleno.echo_characteristic import EchoCharacteristic

class BlenoManager:

    def __init(self, environment):
        self.bleno = Bleno()
        self.environment = environment
        self.bleno.on('stateChange', self.onStateChange)
        self.bleno.on('advertisingStart', self.onAdvertisingStart)

    def start(self):
        print('start bleno')
        self.bleno.start()
    
    def stop(self):
        print('stop bleno')
        self.bleno.stopAdvertising()
        self.bleno.disconnect()

    def onStateChange(self, state):
        print('on -> stateChange: ' + state);

        if (state == 'poweredOn'):
            bleno.startAdvertising('echo', ['ec00'])
        else:
            bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: ' + ('error ' + error if error else 'success'));

        if not error:
            bleno.setServices([
                BlenoPrimaryService({
                    'uuid': self.environment.UUID,
                    'characteristics': [ 
                        EchoCharacteristic('thermometer')
                        ]
                })
            ])

