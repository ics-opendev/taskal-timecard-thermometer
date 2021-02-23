import json

# アプリの環境値
# コマンドラインで指定された値
class ApplicationEnvironment:
    def __init__(self, args_env):
        json_file = open(f'config/env/{args_env}.json', 'r')
        appenv = json.load(json_file)
        self.DEBUG_MODE = bool(appenv['debug_mode'])