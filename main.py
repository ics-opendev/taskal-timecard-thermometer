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
        self.DEVICE_NAME = app_env['deviceName']

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

    # GUIを起動
    from gui.body_temp import BodyTemp
    from bleno.bleno_manager import BlenoManager
    from kivy.config import Config
    app = None
    try:
        bleno_manager = BlenoManager(app_env)
        bleno_manager.start()
        while True:
            app = BodyTemp(app_env, bleno_manager)
            app.run()
            if not app.restart:
                bleno_manager.stop()
                break
            Config._named_configs.pop('app', None)
    except:
        import traceback
        logger.critical(traceback.format_exc())
        if app:
            app.stop()