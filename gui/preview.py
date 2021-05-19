# coding: utf-8

import numpy as np
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import SlideTransition
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
from kivy.graphics.texture import Texture
from kivy.graphics.instructions import InstructionGroup

from gui.param import gParam
from gui.util import get_app, get_home_dir, is_controller

class PreviewScreen(Screen):
    def __init__(self, app, **kwargs):
        super(PreviewScreen, self).__init__(**kwargs)

        self.operating_mode = app.operating_mode

        layoutPreview = FloatLayout()
        layoutSideBar = BoxLayout(orientation = 'vertical', size_hint = (1/3, 1))
        layoutThreshold = BoxLayout(orientation = 'vertical')

        self.preview = Image(allow_stretch = True, keep_ratio = True,
                pos_hint = {'x': 0})
        self.preview.size = (240, 240)
        self.labelInfo = Label(font_size = '48sp', markup = True,
                outline_color = [0, 0, 0], outline_width = 2)
        self.labelInfo2 = Label(font_size = '48sp', markup = True,
                outline_color = [0, 0, 0], outline_width = 2,
                pos_hint = {'center_y': 0.8})

        layoutPreview.add_widget(self.preview)
        layoutPreview.add_widget(Image(allow_stretch = True, keep_ratio = True,
                source = os.path.join(get_home_dir(), 'gui/human_frame.png')))

        layoutPreview.add_widget(self.labelInfo)
        layoutPreview.add_widget(self.labelInfo2)
        self.labelTemp = Label(font_size = '64sp', markup = True,
                outline_color = [0, 0, 0], outline_width = 2)
        layoutPreview.add_widget(self.labelTemp)

        self.labelObsTemps = []
        for i in range(0, 3):
            labelObsTemp = Label(font_size = '32sp', markup = True,
                    halign = 'left', outline_color = [0, 0, 0], outline_width = 2)
            self.labelObsTemps.append(labelObsTemp)
            layoutPreview.add_widget(labelObsTemp)

        self.labelThreshold = Label(font_size = '24sp', markup = True, outline_width = 2)
        layoutThreshold.add_widget(Button(text = '+', font_size = '48sp',
                on_release = self.callback_button))
        layoutThreshold.add_widget(self.labelThreshold)
        layoutThreshold.add_widget(Button(text = '-', font_size = '48sp',
                on_release = self.callback_button))
        correctButton = Button(text = '補正', font_size = '24sp',
                size_hint = (1, 1/3), on_release = self.callback_correct)
        settingsButton = Button(text = '設定', font_size = '24sp',
                size_hint = (1, 1/3), on_release = self.callback_next)
        #layoutSideBar.add_widget(layoutThreshold)
        layoutSideBar.add_widget(correctButton)
        #if self.operating_mode == gParam.OPE_MODE_ALONE:
        #    layoutSideBar.add_widget(settingsButton)

        layoutScreen = None

        if self.operating_mode == gParam.OPE_MODE_GUEST:
            self.bar_color = (0, 0, 0, 1)
            self.color_texture = Texture.create(size = (1, 1), \
                    colorfmt = 'bgra')
            self.color_texture.blit_buffer(b'\x00\x00\x00x00')
            self.color_image = [None, None]
            for i in (0, 1):
                self.color_image[i] = Image(allow_stretch = True, keep_ratio = False, \
                        size_hint_x = 1/7)
                self.color_image[i].texture = self.color_texture
            layoutScreen = BoxLayout(orientation = 'horizontal')
            layoutScreen.add_widget(self.color_image[0])
            layoutScreen.add_widget(layoutPreview)
            layoutScreen.add_widget(self.color_image[1])
        else:
            layoutScreen = BoxLayout(orientation = 'horizontal')
            layoutScreen.add_widget(layoutPreview)
            layoutScreen.add_widget(layoutSideBar)

        self.add_widget(layoutScreen)

        # 黒画像で初期化
        app.textures = [None, None]
        zeros = np.zeros(app.wx * app.wy * 4, dtype = np.uint8)
        for i in (0, 1):
            texture = Texture.create(size =(app.wx, app.wy), \
                    colorfmt = 'bgra', bufferfmt = 'ubyte')
            texture.blit_buffer(zeros)
            texture.flip_vertical()
            app.textures[i] = texture
        app.texture_idx = 0
        self.preview.texture = app.textures[app.texture_idx]

    def on_pre_enter(self):
        self.labelThreshold.text = '[b]{:.1f}[/b]'.format(gParam.TempThreshold)

    def on_touch_up(self, touch):
        super(PreviewScreen, self).on_touch_up(touch)
        get_app().stop_alarm()
        if self.operating_mode == gParam.OPE_MODE_GUEST:
            self.manager.transition = SlideTransition(direction = 'left')
            self.manager.current = 'Settings'

    def on_size(self, instance, value):
        if self.preview.size[0] == 100:
            return
        tx, ty, wh, xr = self.get_temp_pos()
        self.labelTemp.pos = (tx, ty)
        for i in range(0, 3):
            ox = xr * 32 * 2
            oy = 0.25 * (1 - i) * wh
            self.labelObsTemps[i].pos = (ox, oy)

        if not is_controller():
            f32 = '{:d}sp'.format(int(32 * xr))
            f48 = '{:d}sp'.format(int(48 * xr))
            f64 = '{:d}sp'.format(int(64 * xr))
            self.labelInfo.font_size = f48
            self.labelInfo2.font_size = f48
            self.labelTemp.font_size = f64
            for labelObsTemp in self.labelObsTemps:
                labelObsTemp.font_size = f32

    def callback_button(self, button):
        if button.text == '+':
            gParam.TempThreshold += 0.1
        else:
            gParam.TempThreshold -= 0.1
        self.labelThreshold.text = '[b]{:.1f}[/b]'.format(gParam.TempThreshold)
        if self.operating_mode != gParam.OPE_MODE_STAFF:
            gParam.save()
        else:
            url = get_app().url_settings + '?TempThreshold=' + str(gParam.TempThreshold)
            get_app().client_request(url)

    def callback_next(self, instance):
        self.manager.transition = SlideTransition(direction = 'left')
        self.manager.current = 'Settings'

    def callback_correct(self, instance):
        get_app().enable_shortcut()
        self.manager.transition = SlideTransition(direction = 'left')
        self.manager.current = 'TempCalibration'

    def set_color_bar(self, color):
        if self.operating_mode == gParam.OPE_MODE_GUEST and color != self.bar_color:
            if color == (0, 1, 0, 1):
                self.color_texture.blit_buffer(b'\x00\xFF\x00x00')
            else:
                self.color_texture.blit_buffer(b'\x00\x00\x00x00')
            self.color_image[0].texture = self.color_texture
            self.color_image[1].texture = self.color_texture
            self.bar_color = color

    def get_temp_pos(self):
        wx, wy = Window.size
        wx1 = wx / 4 * 3
        wh = wy if wx1 > wy else wx1
        xr = wh / 240
        tx = int(-wh / 2 + xr * 64 + 2)
        ty = int(-wh / 2 + xr * 64 / 2 + 2)
        return (tx, ty, wh, xr)
