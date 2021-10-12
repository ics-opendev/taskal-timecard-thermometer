from pybleno import *
from bleno.characteristic import BodyTempCharacteristic, ThermometerStatusCharacteristic
class BlenoManager:

    def __init__(self, environment, logger):
        self.inner_bleno = Bleno()
        self.environment = environment
        self.body_temp_chara = BodyTempCharacteristic('ec100001-9999-9999-9999-000000000001', logger)
        self.thermometer_status = ThermometerStatusCharacteristic('ec100001-9999-9999-9999-000000000003')
        self.inner_bleno.on('stateChange', self.onStateChange)
        self.inner_bleno.on('advertisingStart', self.onAdvertisingStart)
        self.inner_bleno.on('advertisingStop', self.onAdvertisingStop)
        self.logger = logger

    def start(self):
        self.logger.debug('start bleno')
        self.inner_bleno.start()
    
    def stop(self):
        self.logger.debug('stop bleno')
        self.inner_bleno.stopAdvertising()
        self.inner_bleno.disconnect()

    def onStateChange(self, state):
        self.logger.debug('on -> stateChange: ' + state)

        if (state == 'poweredOn'):
            self.inner_bleno.startAdvertising(self.environment.DEVICE_NAME, ['ec100001-9999-9999-9999-000000000000'])
        else:
            self.inner_bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        self.logger.debug('on -> advertisingStart: ' + ('error ' + error if error else 'success'))

        if not error:
            self.inner_bleno.setServices([
                BlenoPrimaryService({
                    'uuid': 'ec100001-9999-9999-9999-000000000000',
                    'characteristics': [self.body_temp_chara, self.thermometer_status]
                })
            ])

    def onAdvertisingStop(self):
        self.logger.debug('onAdvertisingStop')

    # 測定に変更があったことを通知
    def updateBodyTemp(self, body_temp):
        # キャラクタステック内で温度情報を確定する
        self.body_temp_chara.updateBodyTemp(body_temp)
    
    # カメラの状態に変化があったことを通知
    def updateThermometerStatus(self, status_code):
        self.logger.debug("更新されました", status_code)
        self.thermometer_status.updateStatus(status_code)

