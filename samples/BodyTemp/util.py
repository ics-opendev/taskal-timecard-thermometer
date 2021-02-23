import distro
import json
from kivy.app import App
import os
import platform
import stat
import time
from turbojpeg import TurboJPEG

g_version = "1.0"
g_kernel_name = None
g_id_name = None

def get_app():
    return App.get_running_app()

def version():
    return g_version

def build_number():
    if not os.path.exists(__file__):
        return ""
    lt = time.localtime(os.stat(__file__)[stat.ST_MTIME])
    return "{}{:02d}{:02d}{:02d}".format(lt.tm_year - 2000, lt.tm_mon, lt.tm_mday, lt.tm_hour)

def _ensure_platform_codes():
    global g_kernel_name, g_id_name

    if g_kernel_name:
        return

    g_kernel_name = platform.uname()[0]
    if g_kernel_name == "Linux":
        g_id_name, _, _ = distro.linux_distribution(full_distribution_name=False)

def is_raspbian():
    _ensure_platform_codes()
    return g_id_name == "raspbian"

def is_windows():
    _ensure_platform_codes()
    return g_kernel_name == "Windows"

def is_linux():
    _ensure_platform_codes()
    return g_kernel_name == "Linux"

def is_controller():
    return os.environ.get('BODY_TEMP_CONTROLLER') == "1"

def get_project_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_home_dir():
    home = os.environ.get('BODY_TEMP_HOME')
    if home:
        return home
    return get_project_dir()

def create_turbo_jpeg():
    if is_raspbian():
        return TurboJPEG(os.path.join(get_project_dir(), "lib/armv7l/libturbojpeg.so"))
    return TurboJPEG()

def get_connect_opts():
    connect_opts_path = os.path.join(get_home_dir(), 'connect.txt')

    if not os.path.exists(connect_opts_path):
        return None

    print('load {}'.format(connect_opts_path))
    with open(connect_opts_path, "r", encoding = "utf-8") as f:
        opts = json.loads(f.read())

    return opts

