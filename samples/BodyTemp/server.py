# coding: utf-8

import base64
import json
from flask import Flask, make_response, request
import logging
import numpy as np
import pickle
import threading
import time
from turbojpeg import TJPF_BGRA

from owlifttypeh import OwhDevice, OwhMeta
from util import get_app, create_turbo_jpeg
from param import gParam

class Server(threading.Thread):

    def __init__(self, app):
        super(Server, self).__init__()
        self.setDaemon(True)

        self.webapp = Flask(__name__)
        self.webapp.add_url_rule('/capture', 'capture', self.capture)
        self.webapp.add_url_rule('/settings', 'settings', self.settings)
        self.jpeg = create_turbo_jpeg()
        self.fc0 = 0
        self.wx = app.wx
        self.wy = app.wy
        zeros = np.zeros(self.wx * self.wy * 4, dtype = np.uint8)
        self.img = self.jpeg.encode(zeros.reshape(self.wy, self.wx, 4), pixel_format = TJPF_BGRA)

        log = logging.getLogger('werkzeug')
        log.disabled = True

    def capture(self):
        app = get_app()

        while app.server_fc == app.client_fc:
            time.sleep(0.05)

        img, meta = app.last_frame
        app.client_fc = app.server_fc

        if app.force_observe:
            meta._status = OwhMeta.S_OK

        img_array = np.frombuffer(img, dtype = 'uint8')
        img_jpeg = self.jpeg.encode(img_array.reshape(self.wy, self.wx, 4), pixel_format = TJPF_BGRA)
        response = make_response(img_jpeg)
        response.headers['Content-Type'] = 'image/jpeg'
        response.headers['Content-Length'] = str(len(img_jpeg))
        response.headers['OwhMeta'] = base64.b64encode(pickle.dumps(meta))

        return response

    def settings(self):
        TempThreshold = request.args.get('TempThreshold')
        TempCalibration = request.args.get('TempCalibration')
        CorrectMode = request.args.get('CorrectMode')
        if TempThreshold is not None:
            self.TempThreshold = float(TempThreshold)
            if self.TempThreshold != gParam.TempThreshold:
                gParam.TempThreshold = self.TempThreshold
                gParam.save()
        if TempCalibration is not None:
            self.TempCalibration = float(TempCalibration)
            if self.TempCalibration != gParam.TempCalibration:
                gParam.TempCalibration = self.TempCalibration
                gParam.save()
            get_app().set_manual_body_temp(self.TempCalibration)
        if CorrectMode == 'Start':
            get_app().start_correct_mode()

        d = {'TempThreshold': gParam.TempThreshold, 'TempCalibration': gParam.TempCalibration}
        response = make_response(json.dumps(d))
        response.headers['Content-Type'] = 'application/json'

        return response

    def run(self):
        self.webapp.run(host = '0.0.0.0', port = gParam.Port)
