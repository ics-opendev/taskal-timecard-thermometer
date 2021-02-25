# coding: utf-8

import os
import numpy as np
import threading
import queue
import time

from gui.util import is_controller

if is_controller():
    import RPi.GPIO as GPIO
else:
    from kivy.core.audio import SoundLoader

if is_controller():
    alarm0 = np.array([[0, 1, 240]])
    alarm1 = np.array([[1174.66, 0.5, 240],[0, 0.5, 240]])
    alarm2 = np.array([[1174.66, 0.5, 240],[1174.66, 0.5, 240],[1174.66, 1, 240]])
    alarm3 = np.array([[1174.66, 1, 240],[1174.66, 1, 240],[0, 1, 240]])
    alarm4 = np.array([[1174.66, 2, 240],[1174.66, 2, 240],[1174.66, 2, 240],[0, 2, 240]])
    alarm5 = np.array([[1174.66, 0.5, 240],[1046.50, 0.5, 240]])
    alarm6 = np.array([[1174.66, 0.5, 240],[1046.50, 0.5, 240],[1046.50, 1, 240]])
    alarm7 = np.array([[1174.66, 1, 240],[1046.50, 1, 240]])
    alarm8  = np.array([[1174.66, 1, 240],[1318.51, 1, 240],[1244.51, 1, 240]])
    alarm9 = np.array([[1174.66, 0.5, 240],[1244.51, 0.5, 240],[1318.51, 0.5, 240],[0, 0.5, 240]])
    alarm10 = np.array([[1174.66, 0.5, 240],[1244.51, 0.5, 240],[1318.51, 0.5, 240],[1396.91, 0.5, 240],[1479.98, 0.5, 240],[0, 0.5, 240]])
    passed = np.array([[6272, 0.3, 240],[4699, 0.3, 240]])
    gAlarmList = [alarm0, alarm1, alarm2, alarm3, alarm4, alarm5, alarm6, alarm7, alarm8, alarm9, alarm10]
else:
    gAlarmList = ['alarm0.wav', 'alarm1.wav', 'alarm2.wav', 'alarm3.wav', 'alarm4.wav', 'alarm5.wav', 'alarm6.wav', 'alarm7.wav', 'alarm8.wav', 'alarm9.wav', 'alarm10.wav']
    gAlarmFolder = os.environ['KIVY_HOME'] + '/sound'

class Alarm(threading.Thread):
    EV_STOP = -1
    EV_EXIT = -2
    EV_PASS = -3

    def __init__(self):
        super(Alarm, self).__init__()

        self.queue = queue.Queue()
        self.eid = 0

    def wait(self, sec, eid):
        t = time.perf_counter() + sec
        while (time.perf_counter() < t) and (eid == self.eid):
            pass

    def tone(self, freq, beats, bpm, eid):
        sec = (beats * 60) / bpm
        if freq > 0:
            self.pwm.ChangeFrequency(freq)
            self.pwm.ChangeDutyCycle(50)
            self.wait(sec/2, eid)
            self.pwm.ChangeDutyCycle(0)
            self.wait(sec/2, eid)
        else:
            self.wait(sec, eid)

    def play(self, pattern):
        eid = self.eid
        if is_controller():
            if pattern == self.EV_PASS:
                alarm = passed
            else:
                alarm = gAlarmList[pattern]
            self.pwm.stop()
            while eid == self.eid:
                self.pwm.start(0)
                for data in alarm:
                    if eid != self.eid:
                        break
                    self.tone(data[0], data[1], data[2], eid)
                self.pwm.stop()
                if pattern == self.EV_PASS:
                    break
        else:
            if pattern == self.EV_PASS:
                alarm = gAlarmFolder + '/' + 'ok.wav'
            else:
                alarm = gAlarmFolder + '/' + gAlarmList[pattern]
            sound = SoundLoader.load(alarm)
            sound.play()
            while eid == self.eid:
                if sound.state == 'play':
                    time.sleep(0.1)
                    continue
                if pattern == self.EV_PASS:
                    break
                sound.play()
            sound.stop()
            sound.unload()

    def run(self):
        if is_controller():
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            self.channel = 13
            GPIO.setup(self.channel, GPIO.OUT)
            self.pwm = GPIO.PWM(self.channel, 1)
            self.pwm.start(0)

        while True:
            pattern = self.queue.get()
            if self.queue.empty() == False:
                continue
            if pattern == self.EV_EXIT:
                break
            if pattern == self.EV_STOP:
                continue
            if pattern == 0:
                continue
            self.play(pattern)

        if is_controller():
            GPIO.cleanup()

    def trigger(self, pattern):
        self.queue.put(pattern)
        self.eid += 1

    def cancel(self):
        self.queue.put(self.EV_STOP)
        self.eid += 1

    def passed(self):
        self.queue.put(self.EV_PASS)
        self.eid += 1

    def stop(self):
        self.queue.put(self.EV_EXIT)
        self.eid += 1
