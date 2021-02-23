import time
from owlifttypeh import OwhDevice, OwhLedStat

ow = OwhDevice.connect()

ow.set_led(OwhLedStat.ON, OwhLedStat.ON, OwhLedStat.ON, OwhLedStat.ON)
time.sleep(2)
ow.set_led(OwhLedStat.OFF, OwhLedStat.ON, OwhLedStat.OFF, OwhLedStat.ON)
time.sleep(2)
ow.set_led(OwhLedStat.ON, OwhLedStat.OFF, OwhLedStat.ON, OwhLedStat.OFF)
time.sleep(1)
ow.set_led(OwhLedStat.OFF, OwhLedStat.OFF, OwhLedStat.OFF, OwhLedStat.OFF)
time.sleep(1)
ow.set_led(OwhLedStat.FLASH, OwhLedStat.FLASH, OwhLedStat.FLASH, OwhLedStat.FLASH)
time.sleep(2)
ow.set_led(OwhLedStat.BLINK_ON, OwhLedStat.BLINK_ON, OwhLedStat.BLINK_ON, OwhLedStat.BLINK_ON)
time.sleep(3)
ow.set_led(OwhLedStat.BLINK_ON, OwhLedStat.BLINK_OFF, OwhLedStat.BLINK_ON, OwhLedStat.BLINK_OFF)
time.sleep(3)
ow.set_led(OwhLedStat.OFF, OwhLedStat.OFF, OwhLedStat.OFF, OwhLedStat.OFF)
