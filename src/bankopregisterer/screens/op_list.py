
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

class OpEditButton(Button):
    """Operation edit button"""

    def __init__(self, app: BankOpRegisterer, operation: Operation, **kwargs):

        super().__init__(**kwargs)
        self.app = app
        self.operation = operation

    def on_release(self):
        self.app.op_screen.operation = self.operation
        self.app.screen_mgr.current = OpScreen.NAME
        super().on_release()

class ConfirmPopup(Popup):
    """Confirmation popup"""

    def __init__(self, title: str):
        super().__init__(title=title, size_hint=(None, None), size=(dp(300), dp(150)))
        self.status = False
        layout = BoxLayout()
        layout.orientation = "horizontal"
        layout.add_widget(Button(text="Cancel", size_hint=(0.3, 1), on_release=self.dismiss))
        layout.add_widget(Button(text="Confirm", size_hint=(0.3, 1), on_release=self.confirm))
        self.content = layout

    def confirm(self, dt):
        """Confirm"""
        _ = dt
        self.status = True
        self.dismiss()

class OpDeleteButton(Button):
    """Operation delete button"""

    def __init__(self, app: BankOpRegisterer, operation: Operation, **kwargs):

        super().__init__(**kwargs)
        self.app = app
        self.operation = operation
        self.confirm_popup = ConfirmPopup("Delete operation")
        self.confirm_popup.on_dismiss=self.confirm_popup_dismiss_cb

    def confirm_popup_dismiss_cb(self):
        """Confirmation popup dismiss callback"""
        if self.confirm_popup.status:
            self.app.op_mgr.delete_operation(self.operation)
            self.app.op_mgr.save()
            self.app.op_list_screen.reload()

    def on_release(self):
        self.confirm_popup.open()
        super().on_release()

class OperationLayout(BoxLayout):
    """Operation layout"""

    class _Label(Label):
        def __init__(self, alt_color: bool, **kwargs):
            super().__init__(**kwargs)
            self.alt_color = alt_color
            self.size_hint = (0.7, 1.0)
            self.halign = "left"
            self.valign = "center"
            self.padding_x = dp(10)
            self.font_size = dp(12)
        def on_size(self, *args):
            self.text_size = self.size
            if self.alt_color:
                if self.canvas:
                    self.canvas.before.clear()
                    with self.canvas.before:
                        Color(0.5, 0.5, 0.5, 0.25)
                        Rectangle(pos=self.pos, size=self.size)

    def __init__(self, app: BankOpRegisterer, operation: Operation, alt_color: bool):

        super().__init__()
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.size = (1, dp(35))
        self.add_widget(OperationLayout._Label(alt_color, text=str(operation)))
        self.add_widget(OpEditButton(app, operation, text="edit", size_hint=(0.2, 1)))
        self.add_widget(OpDeleteButton(app, operation, text="x", size_hint=(0.1, 1)))

class OpListScreen(Screen):

    NAME = "operation_list"

    def __init__(self, app: BankOpRegisterer, **kwargs):
        super().__init__(**kwargs)
        self.name = self.NAME
        self.app = app
        self.logger = logging.getLogger(self.__class__.__name__)

    def reload(self):
        """Update operations list"""
        self.logger.debug("OpListScreen: reload")
        op_list_layout = self.ids["op_list_layout"]
        op_list_layout.clear_widgets()
        op_list_layout.height = 0

        for idx, operation in enumerate(self.app.op_mgr.op_list):

            alt_color = False
            if idx % 2 != 1:
                alt_color = True

            operation_layout = OperationLayout(self.app, operation, alt_color)
            op_list_layout.add_widget(operation_layout)
            op_list_layout.height += operation_layout.height + dp(5)

    def on_enter(self, *args):
        self.reload()
        super().on_enter(*args)

    def add_btn_cb(self):
        """Add button callback"""
        # self.root.manager.current = "operation"
        # self.app.screen_mgr.current = OpScreen.NAME
        self.app.screen_mgr.current = "operation"

from bankopregisterer.app import BankOpRegisterer
from bankopregisterer.internal.operation import Operation
from bankopregisterer.screens.operation import OpScreen
