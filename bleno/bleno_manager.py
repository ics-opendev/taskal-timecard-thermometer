from pybleno import *
import sys
import signal
from bleno.characteristic import BodyTempCharacteristic, HumanDetectionCharacteristic, ThermometerStatusCharacteristic
import math

class BlenoManager:

    def __init__(self, environment):
        self.inner_bleno = Bleno()
        self.environment = environment
        self.body_temp_chara = BodyTempCharacteristic('ec100001-9999-9999-9999-000000000001')
        self.human_detection = HumanDetectionCharacteristic('ec100001-9999-9999-9999-000000000002')
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
            self.inner_bleno.startAdvertising(self.environment.DEVICE_NAME, ['ec100001-9999-9999-9999-000000000001', 'ec100001-9999-9999-9999-000000000002', 'ec100001-9999-9999-9999-000000000003'])
        else:
            self.inner_bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: ' + ('error ' + error if error else 'success'));

        if not error:
            self.inner_bleno.setServices([
                BlenoPrimaryService({
                    'uuid': 'ec100001-9999-9999-9999-000000000000',
                    'characteristics': [self.body_temp_chara, self.human_detection, self.thermometer_status]
                })
            ])

    # 測定に変更があったことを通知
    def updateBodyTemp(self, meta):
        # 測定体温
        body_temp = math.floor(meta.body_temp * 10) / 10
        # 測定距離
        distance = meta.distance
        # 購読者に展開
        self.body_temp_chara.updateBodyTemp(body_temp, distance)

    # 人の検出状況に変更があったことを通知
    def updateHumanDetection(self, human_is_detection):
        self.human_detection.updateHumanDetection(human_is_detection)
    
    # カメラの状態に変化があったことを通知
    def updateThermometerStatus(self, status_code, message):
        self.thermometer_status.updateStatus(status_code, message)

