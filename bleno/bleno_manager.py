from pybleno import *
import sys
import signal
from bleno.characteristic import BodyTempCharacteristic, ThermometerStatusCharacteristic
import math

class BlenoManager:

    def __init__(self, environment):
        self.inner_bleno = Bleno()
        self.environment = environment
        self.body_temp_chara = BodyTempCharacteristic('ec100001-9999-9999-9999-000000000001')
        self.thermometer_status = ThermometerStatusCharacteristic('ec100001-9999-9999-9999-000000000003')
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
            self.inner_bleno.startAdvertising(self.environment.DEVICE_NAME, ['ec100001-9999-9999-9999-000000000000'])
        else:
            self.inner_bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: ' + ('error ' + error if error else 'success'));

        if not error:
            self.inner_bleno.setServices([
                BlenoPrimaryService({
                    'uuid': 'ec100001-9999-9999-9999-000000000000',
                    'characteristics': [self.body_temp_chara, self.thermometer_status]
                })
            ])

    # 測定に変更があったことを通知
    def updateBodyTemp(self, body_temp):
        # キャラクタステック内で温度情報を確定する
        self.body_temp_chara.updateBodyTemp(body_temp)
    
    # カメラの状態に変化があったことを通知
    def updateThermometerStatus(self, status_code):
        self.thermometer_status.updateStatus(status_code)

