# coding: utf-8

import os
import shutil
import sqlite3
import threading
import queue

from gui.util import get_home_dir, get_project_dir, is_raspbian

class DType:
    str = 0
    bool = 1
    int = 2
    float = 3

class DBProp:
    def __init__(self, name, defval = "", dtype = DType.str, encrypt = False):
        self.name = name
        self.defval = defval
        self.dtype = dtype
        self.encrypt = encrypt

class DB:
    OPE_MODE_ALONE = 0
    OPE_MODE_GUEST = 1
    OPE_MODE_STAFF = 2

    PROPS = [ \
        DBProp("Server",                "192.168.221.1"),
        DBProp("TempThreshold",         42.5,   dtype = DType.float),
        DBProp("TempCalibration",       36.8,   dtype = DType.float),
        DBProp("TempAverage",           0,      dtype = DType.float),
        DBProp("TempDisplay",           True,   dtype = DType.bool),
        DBProp("AlarmPattern",          0,      dtype = DType.int),
        DBProp("OperatingMode",         0,      dtype = DType.int),
        DBProp("ManuCorr",              4.0,    dtype = DType.float),
        DBProp("ManuCorrRef",           25.0,   dtype = DType.float),
    ]

    def __init__(self):
        self._event = threading.Event()
        self._queue = queue.Queue()
        self._th = threading.Thread(target = self.worker)
        self._th.setDaemon(True)
        self._th.start()
        self._event.wait()

    def worker(self):
        self._init()
        self._event.set()
        while True:
            event = self._queue.get()
            if event == 'load':
                self._load()
            elif event == 'save':
                self._save()
            elif event == 'reset':
                self._reset()
            self._queue.task_done()

    def _init(self):
        home_dir = get_home_dir()
        db_file = home_dir + "/config/db.sqlite3"
        created = False
        if not os.path.exists(db_file):
            shutil.copyfile(get_home_dir() + "/config/db.sqlite3.tmpl", db_file)
            created = True

        self._config = {}
        self._new_config = {}
        self._conn = sqlite3.connect(db_file, isolation_level = "DEFERRED")
        self._cur = self._conn.cursor()

        self._props = {}
        for prop in DB.PROPS:
            self._props[prop.name] = prop

        if created:
            self.complete_by_default()
            self._commit()

    def _set_config(self, name, value):
        self._conn.execute("REPLACE INTO config VALUES (?,?)", (name, value))

    def _get_config(self, name):
        self._cur.execute("SELECT value FROM config WHERE name=?", (name,))
        values = self._cur.fetchone()
        return values[0] if values else ""

    def _commit(self):
        self._conn.commit()
        if is_raspbian():
            os.sync()

    def _rollback(self):
        self._conn.rollback()

    def complete_by_default(self):
        for prop in DB.PROPS:
            self.__setattr__(prop.name, prop.defval)
        self.__save()

    def get_defaults(self):
        vals = {}
        for prop in DB.PROPS:
            vals[prop.name] = prop.defval
        return vals

    def _encrypt(self, dec):
        l = len(dec)
        i = 0
        mask = ""
        while i < l:
            # 48:'0', 122:'z'
            mask += chr(48 + int(random.random() * (122 - 48 + 1)))
            i += 1

        return mask.encode().hex() + "".join([chr(ord(b) ^ ord(m)) \
            for (b, m) in zip(dec, mask)]).encode().hex()

    def _decrypt(self, enc):
        l = int(len(enc) / 2)
        encb = bytes.fromhex(enc[l:]).decode()
        mask = bytes.fromhex(enc[:l]).decode()
        return "".join([chr(ord(b) ^ ord(m))
            for (b, m) in zip(encb, mask)])

    def load(self):
        self._queue.put('load')
        self._queue.join()

    def _load(self):
        for prop in DB.PROPS:
            value = self._get_config(prop.name)
            if prop.dtype == DType.bool:
                value = value == "1"
            elif prop.dtype == DType.int:
                value = int(value)
            elif prop.dtype == DType.float:
                value = float(value)
            if prop.encrypt:
                value = self._decrypt(value)
            self._config[prop.name] = value

        self._new_config.clear()

    def save(self):
        self._queue.put('save')
        self._queue.join()

    def _save(self):
        ok = False
        try:
            self.__save()
            ok = True
        except Exception as e:
            import traceback
            traceback.print_exc()
        finally:
            if ok:
                self._commit()
            else:
                self._rollback()

    def __save(self):
        for name, new_value in self._new_config.items():
            prop = self._props[name]

            if prop.dtype == DType.str:
                new_value = new_value.strip()

            if prop.encrypt:
                db_value = self._encrypt(new_value)
            else:
                db_value = new_value

            self._set_config(name, db_value)

        self._new_config.clear()

    def reset(self):
        self._queue.put('reset')
        self._queue.join()

    def _reset(self):
        config_backup = self._config
        ok = False
        try:
            self._cur.execute("DELETE FROM config")
            self._config = {}
            self.complete_by_default()
            ok = True
        finally:
            if ok:
                self._commit()
            else:
                self._rollback()
                self._config = config_backup

    def __getattr__(self, key):
        # check key is existing
        prop = self._props[key]
        if not key in self._config:
            return ""
        return self._config[key]

    def __setattr__(self, key, val):
        if key[0] == '_':
            return super.__setattr__(self, key, val)
        # check key is existing
        prop = self._props[key]
        self._config[key] = val
        self._new_config[key] = val

gParam = DB()

