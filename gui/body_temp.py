# coding: utf-8

import base64
import json
import numpy as np
import sys
import os
import pickle
import socket
from turbojpeg import TJPF_BGRA
from entity.enum.owlift_h_device_status import OwliftHDeviceStatus
from entity.owlift_h_status import OwliftHStatus
from entity.enum.measurement_type import MeasurementType
from logic.body_surface_temperature_calculation_service import BodySurfaceTemperatureCalculationService

if 'KIVY_HOME' not in os.environ:
    os.environ['KIVY_HOME'] = 'gui/kivy'

os.environ['KIVY_AUDIO'] = 'sdl2'

from owlifttypeh import OwhDevice, OwhMeta
from gui.util import is_controller, is_windows, is_linux, is_raspbian, get_connect_opts

if getattr(sys, 'frozen', False):
    os.environ['PATH'] += os.pathsep + os.path.dirname(sys.executable)

owlift_icon = os.environ['KIVY_HOME'] + '/icon/ttc-logo.png'
previous_icon = os.environ['KIVY_HOME'] + '/icon/previous-icon-32.png'

from kivy.config import Config
Config.set('kivy','window_icon', owlift_icon)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('modules', 'touchring', True)
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '240')

if is_controller():
    Config.set('graphics', 'borderless', True)
    Config.set('graphics', 'resizable', False)
    Config.set('graphics', 'fullscreen', True)
    Config.set('graphics', 'show_cursor', False)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window

if is_windows():
    resource_add_path('c:/Windows/Fonts')
    LabelBase.register(DEFAULT_FONT, 'msgothic.ttc')
elif is_linux():
    resource_add_path(os.environ['KIVY_HOME'] + '/font')
    LabelBase.register(DEFAULT_FONT, 'mplus-1p-regular.ttf')

from gui.settings import SettingsScreen
from gui.settings import TemperatureScreen
from gui.settings import SystemScreen
from gui.settings import TempThresholdScreen
from gui.settings import TempCalibrationScreen
from gui.settings import TempAverageScreen
from gui.settings import TempDisplayScreen
from gui.settings import SystemSoftwareInfoScreen
from gui.settings import SystemLicenseInfoScreen
from gui.settings import SystemOperatingModeScreen
from gui.settings import SystemResetSettingsScreen
from gui.settings import SystemRebootScreen
from gui.preview import PreviewScreen
from gui.param import gParam
from bleno.bleno_manager import BlenoManager

# argsのデフォルト値
class MockArgs:
    def __init__(self):
        self.read = False
        self.write = False
        self.interval = 0.116
        self.file0 = "cam0.owi"
        self.file1 = "cam1.owi"
        self.skip = 0

class BodyTemp(App):
    LABEL_NONE = 0
    LABEL_NOT_READY = 1
    LABEL_CORRECT_0 = 2
    LABEL_CORRECT_1 = LABEL_CORRECT_0 + 1
    LABEL_CORRECT_2 = LABEL_CORRECT_0 + 2
    LABEL_CORRECT_3 = LABEL_CORRECT_0 + 3
    LABEL_CORRECT_4 = LABEL_CORRECT_0 + 4
    LABEL_CORRECT_ERR_0 = 10
    LABEL_CORRECT_ERR_TOO_HIGH = LABEL_CORRECT_ERR_0 + 1
    LABEL_CORRECT_ERR_TOO_LOW = LABEL_CORRECT_ERR_0 + 2
    LABEL_GO_OUT = 13
    LABEL_END_CORRECT = 14
    LABEL_CONNECTING = 15
    LABEL_CONNECT_ERR = 16
    LABEL_COMMUNICATION_ERR = 17
    LABEL_DEV_CONNECT_ERR = 18
    LABEL_DIST_VALID = 19

    LABELS = {
        LABEL_NONE: '',
        LABEL_NOT_READY: '準備中',
        LABEL_CORRECT_1: 'あと1回\n計ります',
        LABEL_CORRECT_2: 'あと2回\n計ります',
        LABEL_CORRECT_3: 'あと3回\n計ります',
        LABEL_CORRECT_4: 'あと4回\n計ります',
        LABEL_CORRECT_ERR_TOO_HIGH: "温度が\n高すぎます",
        LABEL_CORRECT_ERR_TOO_LOW: "温度が\n低すぎます",
        LABEL_GO_OUT: '枠の外に\n出て下さい',
        LABEL_END_CORRECT: '補正が完了\nしました',
        LABEL_CONNECTING: '接続中',
        LABEL_CONNECT_ERR: '接続ｴﾗｰ',
        LABEL_COMMUNICATION_ERR: '通信ｴﾗｰ',
        LABEL_DEV_CONNECT_ERR: 'ｶﾒﾗの\n接続ｴﾗｰ\n再起動してください',
        LABEL_DIST_VALID: '計測中',
    }

    CORRECT_CNT = 4
    TEMP_DISP_CNT = 26
    ALARM_CNT = 26
    INFO_DISP_CNT = 26

    # コンストラクター
    def __init__(self, environment, bleno_manager):
        super().__init__()
        self.environment = environment
        self.bleno_manager = bleno_manager
        self.restart = False

    def open_settings(self, *largs):
        pass

    def build(self):

        self.args = MockArgs()

        if os.path.exists("config.txt"):
            with open("config.txt", encoding = "utf-8") as f:
                self.config = json.loads(f.read())
            self.force_observe = self.config["force_observe"] \
                if "force_observe" in self.config else False
        else:
            self.config = {}
            self.force_observe = False

        gParam.load()

        self.operating_mode = gParam.OperatingMode

        # 体表温度の演算を行う
        self.body_surface_temparature_calculation = BodySurfaceTemperatureCalculationService()

        # フルスクリーン
        # Window.fullscreen = 'auto'

        # 温度計画像のサイズ
        self.wx = 120
        self.wy = 120

        self.screenManager = ScreenManager()

        # プレビュー画面
        self.previewScreen = PreviewScreen(self, name = 'Preview')
        self.screenManager.add_widget(self.previewScreen)

        # 設定画面
        self.screenManager.add_widget(SettingsScreen(name = 'Settings'))
        self.screenManager.add_widget(TemperatureScreen(name = 'Temperature'))
        self.screenManager.add_widget(SystemScreen(name = 'System'))

        # 温度
        self.screenManager.add_widget(TempThresholdScreen(name = 'TempThreshold'))
        self.screenManager.add_widget(TempCalibrationScreen(name = 'TempCalibration'))
        self.screenManager.add_widget(TempAverageScreen(name = 'TempAverage'))
        self.screenManager.add_widget(TempDisplayScreen(name = 'TempDisplay'))

        # システム
        self.screenManager.add_widget(SystemSoftwareInfoScreen(name = 'SystemSoftwareInfo'))
        self.screenManager.add_widget(SystemLicenseInfoScreen(name = 'SystemLicenseInfo'))
        self.screenManager.add_widget(SystemOperatingModeScreen(name = 'SystemOperatingMode'))
        self.screenManager.add_widget(SystemResetSettingsScreen(name = 'SystemResetSettings'))
        if is_raspbian():
            self.screenManager.add_widget(SystemRebootScreen(name = 'SystemReboot'))

        # 内部パラメータ
        self.ow = None
        self.eid0 = 0
        self.shortcut = False
        self.correct_cnt = 0
        self.label_id = BodyTemp.LABEL_NONE
        self.label_id2 = BodyTemp.LABEL_NONE
        self.detected = False
        self.temp_disp_cnt = 0
        self.disp_temp = False
        self.info_disp_cnt = 0
        self.last_frame = None

        return self.screenManager

    def get_temp_text(self, temp):
        if temp >= gParam.TempThreshold:
            return '[color=FF0000]{:.1f}[/color]'.format(temp)
        return '{:.1f}'.format(temp)

    # フレーム情報の解析
    def update_frame(self, img, meta, body_temp):
        # ステータスを取得
        st = meta.status

        # NOTE: カメラステータスのステータスをチェック
        # 正常の場合はカメラで検出したイベントを処理
        if st == OwhMeta.S_OK or self.force_observe:
            if self.info_disp_cnt > 0:
                self.info_disp_cnt -= 1
            elif self.correct_cnt == 0:
                self.set_label(BodyTemp.LABEL_NONE)

            
            if body_temp.measurement_type != MeasurementType.NO_MEASUREMENT:
                self.event_dist(meta, True)
                self.event_body_temp(meta)
            else:
                self.event_lost(meta)
                self.event_dist(meta, False)
            
            # イベントに応じた処理
            eid = meta.event_id
            if eid != self.eid0:
                self.eid0 = eid
                evt = meta.event_type
                if (evt & OwhMeta.EV_CORRECT) != 0:
                    # 補正処理中に検出しました
                    self.event_correct(meta)
        elif st == OwhMeta.S_NO_TEMP or st == OwhMeta.S_INVALID_TEMP:
            # カメラを暖気運転中
            self.set_label(BodyTemp.LABEL_NOT_READY)
        else:
            # なんらかのイレギュラーが発生した場合は「準備中」を表示
            # ステータスについては ドキュメント class OwhMetaを参照
            self.set_label(BodyTemp.LABEL_NOT_READY)

        if self.operating_mode == gParam.OPE_MODE_GUEST:
            self.last_frame = (img, meta)

        self.texture_idx = 1 - self.texture_idx
        texture = self.textures[self.texture_idx]
        texture.blit_buffer(img, colorfmt = 'bgra', bufferfmt = 'ubyte')
        self.previewScreen.preview.texture = texture

    # フレームの更新
    def update(self, dt):
        try:
            currentScreen = self.screenManager.current_screen
            if currentScreen != self.previewScreen:
                return

            # デバイスの接続が切れた場合はエラー表示
            if self.ow.disconnected:
                self.set_label(BodyTemp.LABEL_DEV_CONNECT_ERR)
                self.bleno_manager.updateThermometerStatus(OwliftHDeviceStatus.THERMO_LOST)
                # フレームの更新を停止する
                self.update_event.cancel()
                return

            # フレームと詳細の取得
            img, meta = self.ow.get_frame()

            # サーモデバイスのステータス更新
            old_status, new_status = self.update_owlift_h_status(meta, self.owlift_h_status)

            # 必要であればステータス更新を通知
            self.update_device_status_if_necessary(old_status, new_status)
            self.owlift_h_status = new_status

            # 取得した情報を元に体温を演算
            body_temp = self.body_surface_temparature_calculation.execute(meta, gParam.ManuCorr)
            if body_temp.measurement_type != MeasurementType.NO_MEASUREMENT:
                self.bleno_manager.updateBodyTemp(body_temp)

            # フレーム単位の更新処理
            self.update_frame(img, meta, body_temp)
        except Exception as ex:
            print("サーモループでエラー", ex)

    # デバイスステータス更新
    def update_owlift_h_status(self, meta, current_status):
        preparation = False
        new_status = current_status.status

        # 準備状態のチェック
        if meta.status == OwhMeta.S_OK or self.force_observe:
            if current_status.preparation:
                preparation = False
                new_status = OwliftHDeviceStatus.READY
        elif meta.status == OwhMeta.S_NO_TEMP or meta.status == OwhMeta.S_INVALID_TEMP:
            if not current_status.preparation:
                preparation = True
                new_status = OwliftHDeviceStatus.PREPARATION

        return current_status, OwliftHStatus(preparation, new_status)

    # サーモデバイスのステータス更新を通知する
    def update_device_status_if_necessary(self, old, new):
        print(old.status, new.status)
        if old.status is not new.status:
            print("サーモデイバスのステータス更新を通知しました")
            self.bleno_manager.updateThermometerStatus(new.status)

    def enable_shortcut(self):
        """
        プレビュー画面から補正画面へショートカットするときのフラグ。
        """
        self.shortcut = True

    def get_and_reset_shortcut(self):
        r = self.shortcut
        if self.shortcut:
            self.shortcut = False
        return r

    def event_body_temp(self, meta):
        self.set_label2(BodyTemp.LABEL_NONE)
        self.previewScreen.set_color_bar((0, 1, 0, 1))
        if self.detected == False and gParam.AlarmPattern != 0:
            pass
        self.detected = True

    def event_correct(self, meta):
        self.correct_cnt = meta.correct_count
        self.detected = True
        if meta.correct_error:
            self.set_label(BodyTemp.LABEL_CORRECT_ERR_0 + meta.correct_error)
        elif self.correct_cnt > 0:
            self.set_label(BodyTemp.LABEL_GO_OUT)
        else:
            self.set_label(BodyTemp.LABEL_END_CORRECT)
            self.info_disp_cnt = BodyTemp.INFO_DISP_CNT
            gParam.ManuCorr = meta.manu_corr
            gParam.ManuCorrRef = meta.manu_corr_ref
            gParam.save()

    def event_lost(self, meta):
        self.temp_disp_cnt = BodyTemp.TEMP_DISP_CNT
        self.detected = False

        if self.correct_cnt > 0:
            self.set_label(BodyTemp.LABEL_CORRECT_0 + self.correct_cnt)

    def event_dist(self, meta, valid):
        label_id = BodyTemp.LABEL_DIST_VALID if valid else BodyTemp.LABEL_NONE
        self.set_label2(label_id)

    def set_manual_body_temp(self, temp):
        if self.ow is None:
            return
        self.ow.set_options({"manual_body_temp": temp})

    def set_label(self, label_id):
        if self.label_id == label_id:
            return

        self.label_id = label_id
        self.previewScreen.labelInfo.text = BodyTemp.LABELS[label_id]
        self.previewScreen.labelInfo2.text = ''

    def set_label2(self, label_id):
        if self.label_id2 == label_id or self.label_id != BodyTemp.LABEL_NONE:
            return

        self.label_id2 = label_id
        if label_id != BodyTemp.LABEL_NONE:
            text = '[color=ffff00]' + BodyTemp.LABELS[label_id] + '[/color]'
        else:
            text = ''
        self.previewScreen.labelInfo2.text = text

    def start_correct_mode(self):
        self.correct_cnt = BodyTemp.CORRECT_CNT
        if self.ow is not None and self.operating_mode != gParam.OPE_MODE_STAFF:
            # マニュアル補正の開始
            self.ow.set_options({"correct_mode": self.correct_cnt})
        self.set_label(BodyTemp.LABEL_CORRECT_0 + self.correct_cnt)
        for i in range(0, 3):
            self.previewScreen.labelObsTemps[i].text = ''

    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down = self.on_keyboard_down)
        self.keyboard = None

    # キー操作を取得
    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        k = keycode[1]
        
        if k == 'escape':
            self.stop()

        return True

    # カメラの起動処理
    def start_owhdev(self):
        try:
            try:
                self.ow = OwhDevice.connect(get_connect_opts())
                if not self.ow.has_multi_devs:
                    self.set_label(BodyTemp.LABEL_DEV_CONNECT_ERR)
                    self.ow = None
                    return
            except:
                import traceback
                traceback.print_exc()
                self.bleno_manager.updateThermometerStatus(OwliftHDeviceStatus.DISSCONNECTE)
                self.set_label(BodyTemp.LABEL_DEV_CONNECT_ERR)
                return

            options = {}
            if "options" in self.config:
                options.update(self.config["options"])

            options.update({
                "manual_body_temp": gParam.TempCalibration, # 補正設定値
                "manu_corr": gParam.ManuCorr,# 補正値
                "manu_corr_ref": gParam.ManuCorrRef,
                "temp_tab": True,
                "show_target": False,
            })

            print(options)

            self.ow.set_options(options)
            self.owlift_h_status = OwliftHStatus(False, OwliftHDeviceStatus.PREPARATION)
            self.ow.capture_start()

            self.update_event = Clock.schedule_interval(self.update, self.args.interval)
            print("接続成功")
        except Exception as e:
            print(e)
            self.ow = None
            return

    # kivyの関数 https://pyky.github.io/kivy-doc-ja/api-kivy.app.html
    # buildの実行直後に呼び出されるハンドラー
    # デバイスの開始とサウンドサービスの開始を行っている
    def on_start(self):
        if self.operating_mode == gParam.OPE_MODE_ALONE:
            self.start_owhdev()
        elif self.operating_mode == gParam.OPE_MODE_STAFF:
            pass            
        elif self.operating_mode == gParam.OPE_MODE_GUEST:
            self.start_owhdev()
    
    # kivyの関数 https://pyky.github.io/kivy-doc-ja/api-kivy.app.html
    # Windowがクローズされる前に呼び出される
    def on_stop(self):
        pass