# coding: UTF-8
import sys
import argparse
import json
import logging
import logging.handlers
import os

# ロガーを設定 log_levelについては下記を参照
# NOTE: https://docs.python.org/ja/3/library/logging.html#levels
def setup_logger(app_env, modname=__name__):
    logger = logging.getLogger(modname)
    logger.setLevel(app_env.LOG_LEVEL)

    # コンソールに出力
    sh = logging.StreamHandler()
    sh.setLevel(app_env.LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # ファイルに出力 10MB 5ファイル分
    fh = logging.handlers.RotatingFileHandler(app_env.LOG_FILE_PATH, maxBytes=1024 * 1024 * 10 , backupCount=5, encoding='utf-8')
    fh.setLevel(app_env.LOG_LEVEL)
    fh_formatter = logging.Formatter('%(asctime)s - %(filename)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    return logger


# アプリの環境値を保管するクラス
class ApplicationEnvironment:
    def __init__(self, args_env):
        json_file = open(f'config/env/{args_env}.json', 'r')
        app_env = json.load(json_file)
        self.LOG_LEVEL = app_env['log']['level']
        self.LOG_FILE_PATH = app_env['log']['file_path']

# kivyの初期設定
def setup_kivy():
    #環境変数を追加
    if 'KIVY_HOME' not in os.environ:
        os.environ['KIVY_HOME'] = 'gui/kivy'
    os.environ['KIVY_AUDIO'] = 'sdl2'

    # 各種iconPathを設定
    owlift_icon = os.environ['KIVY_HOME'] + '/icon/owlift-icon-32.png'
    previous_icon = os.environ['KIVY_HOME'] + '/icon/previous-icon-32.png'

    
    # kivyのコンフィグを設定
    from kivy.config import Config
    Config.set('kivy','window_icon', owlift_icon)
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    Config.set('modules', 'touchring', True)
    Config.set('graphics', 'width', '320')
    Config.set('graphics', 'height', '240')

    from gui.util import is_controller, is_windows, is_linux
    # タッチスクリーンに対応していれば実行
    if is_controller():
        Config.set('graphics', 'borderless', True)
        Config.set('graphics', 'resizable', False)
        Config.set('graphics', 'fullscreen', True)
        Config.set('graphics', 'show_cursor', False)

    # OS別のフォントを設定
    from kivy.resources import resource_add_path
    from kivy.core.text import LabelBase, DEFAULT_FONT
    if is_windows():
        resource_add_path('c:/Windows/Fonts')
        LabelBase.register(DEFAULT_FONT, 'msgothic.ttc')
    elif is_linux():
        resource_add_path(os.environ['KIVY_HOME'] + '/font')
        LabelBase.register(DEFAULT_FONT, 'mplus-1p-regular.ttf')

# Main関数
if __name__ == '__main__':
    # アプリの実行パスを保存
    os.environ['THERMO_APP_HOME'] = os.path.dirname(os.path.abspath(__file__))

    # コマンドライン引数を検査
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', help='アプリの設定値 (config/env/{--env}) default: local', default='local')
    args = parser.parse_args()
    
    # アプリの設定値を読み込み
    app_env = ApplicationEnvironment(args.env)

    # ロガーの初期化
    logger = setup_logger(app_env)
    logger.debug('アプリの起動')
    logger.debug('アプリの初期化に成功しました')

    # NOTE: kivyのロガーが有効になった後で独自のロガーは定義できないためここで実行
    # kivyの初期設定
    from gui.main_screen import MainScreen
    setup_kivy()

    # GUIアプリの起動
    gui_app = None
    try:
        gui_app = MainScreen()
        gui_app.run()
    except:
        import traceback
        logger.critical(traceback.format_exc())
        if gui_app:
            gui_app.stop()