
from __future__ import annotations

import csv
# from dataclasses import dataclass
from datetime import datetime
# from enum import Enum
import logging
# from os.path import expanduser, dirname, join
from os.path import expanduser
# from typing import Any
from typing import List, Union

import kivy
from kivy.app import App
# from kivy.app import App, user_data_dir
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.lang import Builder
# from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
# from kivy.uix.stacklayout import StackLayout
# from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
# from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.utils import platform

KEY_ESC = 27

kivy.require('2.3.0')

root_widget = Builder.load_file("main.kv")
Window.clearcolor = (0.20, 0.20, 0.20, 1)

class BankOpRegisterer(App):
    """Bank operation registerer app"""

    def __init__(self, base_dir_path: str, **kwargs):
        super().__init__(**kwargs)

        self.logger = logging.getLogger("BankOpRegisterer")

        self.base_dir_path = base_dir_path
        self.logger.debug("BankOpRegisterer: base_dir_path = %s", self.base_dir_path)

        self.op_mgr = OpMgr(f"{base_dir_path}/operation_list.csv")
        self.screen_mgr = ScreenManager()
        self.op_list_screen = OpListScreen(self, name=OpListScreen.NAME)
        self.op_screen = OpScreen(self,name=OpScreen.NAME)

        screen_list = [
            self.op_list_screen,
            self.op_screen,
        ]

        for screen in screen_list:
            self.screen_mgr.add_widget(screen)

        self.screen_mgr.current = OpListScreen.NAME

        Window.bind(on_keyboard=self.keyboard_cb)

    def keyboard_cb(self, window, key, *largs):
        if key == KEY_ESC:
            if self.screen_mgr.current == OpScreen.NAME:
                self.op_screen.exit()
                return True

    def build(self):
        return self.screen_mgr

from internal.op_mgr import OpMgr
from screens.op_list import OpListScreen
from screens.operation import OpScreen
