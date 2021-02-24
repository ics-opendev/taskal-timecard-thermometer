from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from gui.preview import PreviewScreen
from gui.param import gParam

class MainScreen(App):
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
        LABEL_DEV_CONNECT_ERR: 'ｶﾒﾗの\n接続ｴﾗｰ',
        LABEL_DIST_VALID: '計測中',
    }

    CORRECT_CNT = 4
    TEMP_DISP_CNT = 26
    ALARM_CNT = 26
    INFO_DISP_CNT = 26

    # この関数はkivyのオーバライドです
    # 初期画面を作成します
    def build(self):
        self.config = {}
        self.force_observe = False
        gParam.load()

        self.operating_mode = gParam.OperatingMode

        self.wx = 120
        self.wy = 120
        self.screenManager = ScreenManager()

        # プレビュー画面
        self.previewScreen = PreviewScreen(self, name = 'Preview')
        self.screenManager.add_widget(self.previewScreen)



        return self.screenManager