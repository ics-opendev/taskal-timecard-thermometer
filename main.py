import sys
import argparse

# 独自モジュール
from config.application_environment import ApplicationEnvironment

if __name__ == '__main__':
    # コマンドライン引数を検査
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', help='アプリの設定値 (config/env/{--env}) default: local', default='local')
    args = parser.parse_args()
    
    # アプリの設定値を読み込み
    app_env = ApplicationEnvironment(args.env)