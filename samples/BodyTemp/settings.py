# coding: utf-8

import os
import codecs
import json
import math
import numpy as np
import subprocess

import util

previous_icon = os.environ['KIVY_HOME'] + '/icon/previous-icon-32.png'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup

from param import gParam
from util import get_app

class Label24sp(Label):
    def __init__(self, **kwargs):
        super(Label24sp, self).__init__(**kwargs)
        self.font_size = '24sp'

class Label48sp(Label):
    def __init__(self, **kwargs):
        super(Label48sp, self).__init__(**kwargs)
        self.font_size = '48sp'

class Button24sp(Button):
    def __init__(self, **kwargs):
        super(Button24sp, self).__init__(**kwargs)
        self.font_size = '24sp'

class Button48sp(Button):
    def __init__(self, **kwargs):
        super(Button48sp, self).__init__(**kwargs)
        self.font_size = '48sp'

class TempThresholdScreen(Screen):
    def __init__(self, **kwargs):
        super(TempThresholdScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]発熱温度[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Button
        layout = BoxLayout(orientation = 'vertical')
        self.label = Label48sp(markup = True)
        layout.add_widget(self.label)
        layoutButton = GridLayout(cols = 2, rows = 1, size_hint =(1, 1/2))
        layoutButton.add_widget(Button48sp(text = '+', on_release = self.callback_button))
        layoutButton.add_widget(Button48sp(text = '-', on_release = self.callback_button))
        layout.add_widget(layoutButton)
        layoutScreen.add_widget(layout)

        self.add_widget(layoutScreen)

    def on_pre_enter(self):
        self.TempThreshold = gParam.TempThreshold
        self.label.text = '[b]{:.1f} ℃[/b]'.format(self.TempThreshold)

    def callback_button(self, instance):
        if instance.text == '+':
            self.TempThreshold += 0.1
        else:
            self.TempThreshold -= 0.1
        self.label.text = '[b]{:.1f} ℃[/b]'.format(self.TempThreshold)

    def callback_previous(self, instance):
        if self.TempThreshold != gParam.TempThreshold:
            gParam.TempThreshold = self.TempThreshold
            gParam.save()
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Temperature'

class TempCalibrationScreen(Screen):
    def __init__(self, **kwargs):
        super(TempCalibrationScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]基準値[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Button
        layout = BoxLayout(orientation = 'vertical')
        layout2 = BoxLayout(orientation = 'horizontal')
        self.label = Label48sp(markup = True)
        layout2.add_widget(self.label)
        layoutButton = GridLayout(cols = 1, rows = 2, size_hint =(1/3, 1))
        layoutButton.add_widget(Button48sp(text = '+', on_release = self.callback_button))
        layoutButton.add_widget(Button48sp(text = '-', on_release = self.callback_button))
        layout2.add_widget(layoutButton)
        layout.add_widget(layout2)
        layout.add_widget(Button24sp(text = '計測', size_hint =(1, 1/3), on_release = self.callback_preview))
        layoutScreen.add_widget(layout)

        self.add_widget(layoutScreen)

    def on_pre_enter(self):
        self.TempCalibration = gParam.TempCalibration
        self.label.text = '[b]{:.1f} ℃[/b]'.format(self.TempCalibration)
        self.shortcut = get_app().get_and_reset_shortcut()

    def callback_button(self, instance):
        if instance.text == '+':
            self.TempCalibration += 0.1
        else:
            self.TempCalibration -= 0.1
        self.label.text = '[b]{:.1f} ℃[/b]'.format(self.TempCalibration)

    def save(self):
        if self.TempCalibration != gParam.TempCalibration:
            gParam.TempCalibration = self.TempCalibration
            gParam.save()
        get_app().set_manual_body_temp(self.TempCalibration)

    def upload(self, correct_mode):
        url = get_app().url_settings + '?'
        params = []
        if self.TempCalibration != gParam.TempCalibration:
            gParam.TempCalibration = self.TempCalibration
            param = 'TempCalibration=' + str(gParam.TempCalibration)
            params.append(param)
        if correct_mode:
            params.append('CorrectMode=Start')

        if len(params) == 0:
            return
        for param in params:
            url = url + param + '&'

        get_app().client_request(url)

    def callback_previous(self, instance):
        # 戻るボタンのときは計測せず基準値を変更するだけ
        if get_app().operating_mode != gParam.OPE_MODE_STAFF:
            self.save()
        else:
            self.upload(False)
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Preview' if self.shortcut else 'Temperature'

    def callback_preview(self, instance):
        if get_app().operating_mode != gParam.OPE_MODE_STAFF:
            self.save()
        else:
            self.upload(True)
        get_app().start_correct_mode()
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Preview'

class TempAverageScreen(Screen):
    def __init__(self, **kwargs):
        super(TempAverageScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]平均[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Button
        layout = BoxLayout(orientation = 'vertical')
        self.label = Label48sp(markup = True)
        layout.add_widget(self.label)
        layoutButton = GridLayout(cols = 2, rows = 1, size_hint =(1, 1/2))
        layoutButton.add_widget(Button48sp(text = '+', on_release = self.callback_button))
        layoutButton.add_widget(Button48sp(text = '-', on_release = self.callback_button))
        layout.add_widget(layoutButton)
        layoutScreen.add_widget(layout)

        self.add_widget(layoutScreen)

    def on_pre_enter(self):
        self.TempAverage = gParam.TempAverage
        self.label.text = '[b]{}[/b]'.format(self.TempAverage)

    def callback_button(self, instance):
        if instance.text == '+':
            self.TempAverage += 1
        else:
            self.TempAverage -= 1
        self.label.text = '[b]{}[/b]'.format(self.TempAverage)

    def callback_previous(self, instance):
        if self.TempAverage != gParam.TempAverage:
            gParam.TempAverage = self.TempAverage
            gParam.save()
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Temperature'

class TempDisplayScreen(Screen):
    def __init__(self, **kwargs):
        super(TempDisplayScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]温度表示[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Switch
        layoutH = BoxLayout(orientation = 'horizontal')
        layoutH.add_widget(Label(size_hint_y = 1/2))
        self.switch = Switch(size_hint = (1, 1))
        self.switch.bind(active = self.callback_active)
        layoutH.add_widget(self.switch)
        layoutH.add_widget(Label(size_hint_y = 1/2))
        layoutV = BoxLayout(orientation = 'vertical')
        layoutV.add_widget(Label(size_hint_y = 1/2))
        layoutV.add_widget(layoutH)
        layoutV.add_widget(Label(size_hint_y = 1/2))
        layoutScreen.add_widget(layoutV)

        self.add_widget(layoutScreen)

    def on_pre_enter(self):
        self.TempDisplay = gParam.TempDisplay
        self.switch.active = self.TempDisplay

    def callback_active(self, instance, value):
        self.TempDisplay = value

    def callback_previous(self, instance):
        if self.TempDisplay != gParam.TempDisplay:
            gParam.TempDisplay = self.TempDisplay
            gParam.save()
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Temperature'

class TemperatureScreen(Screen):

    d = {
            '発熱温度' : 'TempThreshold',
            '補正' : 'TempCalibration',
            '平均' : 'TempAverage',
            '温度表示' : 'TempDisplay'
        }

    def __init__(self, **kwargs):
        super(TemperatureScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]温度[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Button
        layoutButton = GridLayout(cols = 2, rows = 2)
        buttonThreshold = Button24sp(text = '発熱温度')
        buttonCalibration = Button24sp(text = '補正')
        buttonAverage = Button24sp(text = '平均')
        buttonDisplay = Button24sp(text = '温度表示')
        buttonThreshold.bind(on_release = self.callback_next)
        buttonCalibration.bind(on_release = self.callback_next)
        buttonAverage.bind(on_release = self.callback_next)
        buttonDisplay.bind(on_release = self.callback_next)
        layoutButton.add_widget(buttonThreshold)
        layoutButton.add_widget(buttonCalibration)
        layoutButton.add_widget(buttonAverage)
        layoutButton.add_widget(buttonDisplay)
        layoutScreen.add_widget(layoutButton)

        self.add_widget(layoutScreen)

    def callback_previous(self, instance):
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Settings'

    def callback_next(self, instance):
        self.manager.transition = SlideTransition(direction = 'left')
        self.manager.current = self.d[instance.text]

class DispRotateScreen(Screen):
    def __init__(self, **kwargs):
        super(DispRotateScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]回転[/size]', markup = True)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        #
        layoutScreen.add_widget(Label())

        self.add_widget(layoutScreen)

    def callback_previous(self, instance):
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Display'

class MyCheckBox(CheckBox):
    def __init__(self, **kwargs):
        self.index = kwargs.pop('index')
        super(CheckBox, self).__init__(**kwargs)

class AlarmScreen(Screen):
    def __init__(self, **kwargs):
        super(AlarmScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]警告音[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Radio Button
        scrollView = ScrollView()
        if util.is_controller():
            size_hint = (1, 3.5)
        else:
            size_hint = (1, 1)
        layoutButton = BoxLayout(orientation = 'vertical', size_hint = size_hint)
        self.checkbox = []
        self.index = gParam.AlarmPattern
        if util.is_controller():
            num_pattern = 10
        else:
            num_pattern = 2
        for i in range(0, num_pattern + 1):
            active = False
            if i == self.index:
                active = True
            text = 'ﾊﾟﾀｰﾝ {}'.format(i)
            if i == 0:
                text = 'なし'
            layout = BoxLayout(orientation = 'horizontal')
            checkbox = MyCheckBox(group = 'AlarmPattern', active = active, index = i, size_hint_x = 1/3)
            checkbox.bind(on_press = self.on_press)
            self.checkbox.append(checkbox)
            layout.add_widget(Label(size_hint_x = 1/3))
            layout.add_widget(checkbox)
            layout.add_widget(Label24sp(text = text))
            layoutButton.add_widget(layout)
        if util.is_controller():
            scrollView.add_widget(layoutButton)
            layoutScreen.add_widget(scrollView)
        else:
            layoutScreen.add_widget(layoutButton)

        self.add_widget(layoutScreen)

    def on_pre_enter(self):
        self.AlarmPattern = gParam.AlarmPattern
        if self.index != self.AlarmPattern:
            self.checkbox[self.index].active = False
            self.index = self.AlarmPattern
            self.checkbox[self.index].active = True

    def on_press(self, instance):
        if instance.active == False:
            instance.active = True
        else:
            self.AlarmPattern = instance.index
            self.index = self.AlarmPattern
        get_app().start_alarm(self.AlarmPattern)

    def callback_previous(self, instance):
        if self.AlarmPattern != gParam.AlarmPattern:
            gParam.AlarmPattern = self.AlarmPattern
            gParam.save()
        get_app().stop_alarm()
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Settings'

class SystemSoftwareInfoScreen(Screen):
    def __init__(self, **kwargs):
        super(SystemSoftwareInfoScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]ｿﾌﾄｳｪｱ情報[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Label
        layoutScreen.add_widget(Label24sp(text = 'ﾊﾞｰｼﾞｮﾝ: {}'.format(util.version())))
        layoutScreen.add_widget(Label24sp(text = 'ﾋﾞﾙﾄﾞ番号: {}'.format(util.build_number())))

        self.add_widget(layoutScreen)

    def callback_previous(self, instance):
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'System'

class SystemLicenseInfoScreen(Screen):
    def __init__(self, **kwargs):
        super(SystemLicenseInfoScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]ﾗｲｾﾝｽ情報[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        #
        layoutScreen.add_widget(Label())

        self.add_widget(layoutScreen)

    def callback_previous(self, instance):
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'System'

class SystemOperatingModeScreen(Screen):
    def __init__(self, **kwargs):
        super(SystemOperatingModeScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]動作ﾓｰﾄﾞ[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Radio Button
        layoutButton = BoxLayout(orientation = 'vertical')
        self.checkbox = []
        self.index = gParam.OperatingMode
        for i in range(0, 2):
            active = False
            if i == self.index:
                active = True
            if i == 0:
                text = '単独(ｽﾀﾝﾄﾞｱﾛﾝ)'
            else:
                text = '分離(ｹﾞｽﾄ)    '
            layout = BoxLayout(orientation = 'horizontal')
            checkbox = MyCheckBox(group = 'OperatingMode', active = active, index = i, size_hint_x = 1/3)
            checkbox.bind(on_press = self.on_press)
            self.checkbox.append(checkbox)
            layout.add_widget(Label(size_hint_x = 1/3))
            layout.add_widget(checkbox)
            layout.add_widget(Label24sp(text = text))
            layoutButton.add_widget(layout)
        layoutButton.add_widget(Label(text = '※反映にはｱﾌﾟﾘの再起動が必要です', font_size = '16sp'))
        layoutScreen.add_widget(layoutButton)

        self.add_widget(layoutScreen)

    def on_pre_enter(self):
        self.OperatingMode = gParam.OperatingMode
        if self.index != self.OperatingMode:
            self.checkbox[self.index].active = False
            self.index = self.OperatingMode
            self.checkbox[self.index].active = True

    def on_press(self, instance):
        if instance.active == False:
            instance.active = True
        else:
            self.OperatingMode = instance.index
            self.index = self.OperatingMode
            gParam.OperatingMode = self.OperatingMode
            gParam.save()

    def callback_previous(self, instance):
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'System'

class MyPopup(Popup):
    def __init__(self, **kwargs):
        text = kwargs.pop('text')
        super(MyPopup, self).__init__(**kwargs)

        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(Label24sp(text = text))
        layout.add_widget(Button24sp(text = '閉じる', on_release = self.dismiss))

        self.content = layout
        self.size_hint = (0.75, 0.75)
        self.auto_dismiss = False

class SystemResetSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SystemResetSettingsScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]設定ﾘｾｯﾄ[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Button
        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(Label24sp(text = '設定をﾘｾｯﾄしますか？'))
        layoutButton = GridLayout(cols = 2, rows = 1, size_hint =(1, 1/2))
        layoutButton.add_widget(Button24sp(text = 'はい', on_release = self.callback_reset))
        layoutButton.add_widget(Button24sp(text = 'いいえ', on_release = self.callback_previous))
        layout.add_widget(layoutButton)
        layoutScreen.add_widget(layout)

        self.add_widget(layoutScreen)

        # Popup
        self.popup = MyPopup(title = '設定ﾘｾｯﾄ', text = '設定をﾘｾｯﾄしました')

    def callback_reset(self, instance):
        gParam.reset()
        gParam.save()
        self.popup.open()

    def callback_previous(self, instance):
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'System'

class SystemRebootScreen(Screen):
    def __init__(self, **kwargs):
        super(SystemRebootScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]再起動[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Button
        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(Label24sp(text = '再起動しますか？'))
        layoutButton = GridLayout(cols = 2, rows = 1, size_hint =(1, 1/2))
        layoutButton.add_widget(Button24sp(text = 'はい', on_release = self.callback_reboot))
        layoutButton.add_widget(Button24sp(text = 'いいえ', on_release = self.callback_previous))
        layout.add_widget(layoutButton)
        layoutScreen.add_widget(layout)

        self.add_widget(layoutScreen)

    def callback_reboot(self, instance):
        if util.is_windows():
#            os.system("shutdown -r -t 0")
            pass
        elif util.is_raspbian():
            subprocess.run("./restart.sh", shell = True)
            get_app().stop()

    def callback_previous(self, instance):
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'System'

class SystemScreen(Screen):

    d = {
            'ｿﾌﾄｳｪｱ情報' : 'SystemSoftwareInfo',
            'ﾗｲｾﾝｽ情報' : 'SystemLicenseInfo',
            '動作ﾓｰﾄﾞ' : 'SystemOperatingMode',
            '設定ﾘｾｯﾄ' : 'SystemResetSettings',
        }

    def __init__(self, **kwargs):
        super(SystemScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]ｼｽﾃﾑ[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Button
        layoutButton = GridLayout(cols = 2, rows = 3)
        buttonSoftware = Button24sp(text = 'ｿﾌﾄｳｪｱ情報')
        buttonSoftware.bind(on_release = self.callback_next)
        layoutButton.add_widget(buttonSoftware)
        buttonLicense = Button24sp(text = 'ﾗｲｾﾝｽ情報')
        buttonLicense.bind(on_release = self.callback_next)
        layoutButton.add_widget(buttonLicense)
        buttonMode = Button24sp(text = '動作ﾓｰﾄﾞ')
        buttonMode.bind(on_release = self.callback_next)
        layoutButton.add_widget(buttonMode)
        buttonReset = Button24sp(text = '設定ﾘｾｯﾄ')
        buttonReset.bind(on_release = self.callback_next)
        layoutButton.add_widget(buttonReset)
        if util.is_raspbian():
            buttonReboot = Button24sp(text = '再起動')
            buttonReboot.bind(on_release = self.callback_next)
            layoutButton.add_widget(buttonReboot)

        layoutScreen.add_widget(layoutButton)

        self.add_widget(layoutScreen)

    def callback_previous(self, instance):
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Settings'

    def callback_next(self, instance):
        self.manager.transition = SlideTransition(direction = 'left')
        self.manager.current = self.d[instance.text]

class SettingsScreen(Screen):

    d = {
            '温度' : 'Temperature',
            '警告音' : 'Alarm',
            'ｼｽﾃﾑ' : 'System'
        }

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        layoutScreen = BoxLayout(orientation = 'vertical')

        # ActionBar
        actionBar = ActionBar(size_hint_y = 1/4)
        actionView = ActionView()
        actionPrevious = ActionPrevious(title = '[size=24sp]設定[/size]', markup = True, previous_image = previous_icon)
        actionPrevious.bind(on_release = self.callback_previous)
        actionView.add_widget(actionPrevious)
        actionBar.add_widget(actionView)
        layoutScreen.add_widget(actionBar)

        # Button
        layoutButton = GridLayout(cols = 2, rows = 3)
        buttonTemperature = Button24sp(text = '温度')
        buttonDisplay = Button24sp(text = '表示')
        buttonAlarm = Button24sp(text = '警告音')
        buttonSystem = Button24sp(text = 'ｼｽﾃﾑ')
        buttonTemperature.bind(on_release = self.callback_next)
        buttonDisplay.bind(on_release = self.callback_next)
        buttonAlarm.bind(on_release = self.callback_next)
        buttonSystem.bind(on_release = self.callback_next)
        layoutButton.add_widget(buttonTemperature)
        layoutButton.add_widget(buttonAlarm)
        layoutButton.add_widget(buttonSystem)
        layoutScreen.add_widget(layoutButton)

        self.add_widget(layoutScreen)

    def callback_previous(self, instance):
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'Preview'

    def callback_next(self, instance):
        self.manager.transition = SlideTransition(direction = 'left')
        self.manager.current = self.d[instance.text]
