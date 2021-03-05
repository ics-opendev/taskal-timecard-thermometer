from pybleno import *
import sys
import signal
from bleno.characteristic import BodyTempCharacteristic
from api.taskal_api_client import ThermoStatus

# 体温測定情報
class BodyTempInfo:

    def __init__(self, measured_temperature, measured_distance):
        # 送信するデータ
        self.measured_temperature = measured_temperature
        self.measured_distance = measured_distance

    def __deepcopy__(self):
        deepcopy_obj = BodyTempInfo()
        deepcopy_obj.measured_temperature = self.measured_temperature
        deepcopy_obj.measured_distance = self.measured_distance
        return deepcopy_obj


class BlenoManager:

    def __init__(self, environment):
        self.inner_bleno = Bleno()
        self.environment = environment
        self.body_temp_chara = BodyTempCharacteristic('ec100001-9999-9999-9999-000000000001')
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
            self.inner_bleno.startAdvertising(self.environment.DEVICE_NAME, ['ec100001-9999-9999-9999-000000000001'])
        else:
            self.inner_bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: ' + ('error ' + error if error else 'success'));

        if not error:
            self.inner_bleno.setServices([
                BlenoPrimaryService({
                    'uuid': 'ec100001-9999-9999-9999-000000000001',
                    'characteristics': [self.body_temp_chara]
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

