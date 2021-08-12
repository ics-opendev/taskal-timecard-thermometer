# coding: UTF-8
import sys
import argparse
import json
import logging
import logging.handlers
import os

# 体温温度演算サービス
class BodySurfaceTemperatureCalculationService:
    def __init__(self):
        pass
    
    # 体表温度の演算を行う（演算結果、UIの変更箇所)
    def execute(self, img, meta):
        # ステータスを取得
        current_status = meta.status
        # 生の測定情報
        temp_table = meta.temp_tab

        # NOTE: カメラステータスのステータスをチェック
        # 正常の場合はカメラで検出したイベントを処理
        if current_status == OwhMeta.S_OK or self.force_observe:
            if self.thermometer_preparation:
                # 準備が完了していることを通知
                self.thermometer_preparation = False
                self.bleno_manager.updateThermometerStatus(BodyTemp.READY)

            if self.info_disp_cnt > 0:
                self.info_disp_cnt -= 1
            elif self.correct_cnt == 0:
                self.set_label(BodyTemp.LABEL_NONE)

            # 人を検出した場合は、取得箇所の温度を表示
            if self.correct_cnt == 0 and self.disp_temp and not self.detected \
                and meta.obs_temps is not None \
                and self.operating_mode != gParam.OPE_MODE_GUEST:
                i = 0
                for t in meta.obs_temps:
                    self.previewScreen.labelObsTemps[i].text = self.get_temp_text(t) if t > 0 else ''
                    i += 1
            else:
                for i in range(0, 3):
                    self.previewScreen.labelObsTemps[i].text = ''

            # イベントに応じた処理
            eid = meta.event_id
            if eid != self.eid0:
                self.eid0 = eid
                evt = meta.event_type
                if (evt & OwhMeta.EV_BODY_TEMP) != 0:
                    # 発見した人から体温を検出しました
                    self.event_body_temp(meta)
                    self.bleno_manager.updateBodyTemp(meta)
                    # 実体温を表示
                    max_temp = np.max(meta.temp_tab)
                    print(meta.temp_tab)
                    #print("{:.1f}".format(max_temp - 273.15))
                if (evt & OwhMeta.EV_CORRECT) != 0:
                    # 補正処理中に検出しました
                    self.event_correct(meta)
                if (evt & OwhMeta.EV_LOST) != 0:
                    # 人が消えた
                    self.event_lost(meta)
                    self.bleno_manager.updateHumanDetection(str(False))
                if (evt & OwhMeta.EV_DIST_VALID) != 0:
                    # 人を検出しました
                    self.event_dist(meta, True)
                    print("人を検出しました")
                    self.bleno_manager.updateHumanDetection(str(True))
                if (evt & OwhMeta.EV_DIST_INVALID) != 0:
                    # 計測範囲外に出ました
                    self.event_dist(meta, False)
        elif st == OwhMeta.S_NO_TEMP or st == OwhMeta.S_INVALID_TEMP:
            # カメラを暖気運転中
            self.set_label(BodyTemp.LABEL_NOT_READY)
            
            # 準備中を通知
            if not self.thermometer_preparation:
                # 準備が完了していることを通知
                self.thermometer_preparation = True
                self.bleno_manager.updateThermometerStatus(BodyTemp.PREPARATION)
        else:
            # なんらかのイレギュラーが発生した場合は「準備中」を表示
            # ステータスについては ドキュメント class OwhMetaを参照
            self.set_label(BodyTemp.LABEL_NOT_READY)

        if not self.detected and self.temp_disp_cnt > 0:
            self.temp_disp_cnt -= 1
            if self.temp_disp_cnt == 0:
                self.previewScreen.labelTemp.text = ''
                self.previewScreen.set_color_bar((0, 0, 0, 1))

        self.texture_idx = 1 - self.texture_idx
        texture = self.textures[self.texture_idx]
        texture.blit_buffer(img, \
                colorfmt = 'bgra', bufferfmt = 'ubyte')

        if self.operating_mode == gParam.OPE_MODE_GUEST:
            self.last_frame = (img, meta)
            self.server_fc = self.fc0

        self.previewScreen.preview.texture = texture