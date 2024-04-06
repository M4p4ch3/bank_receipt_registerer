
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

class OpScreen(Screen):

    class ModeField(BoxLayout):

        class Drop(DropDown):

            class _Button(Button):

                def __init__(self, name: str, op_field_mode: OpScreen.ModeField, **kwargs):
                    super().__init__(text=name, **kwargs)
                    self.id = name
                    self.name = name
                    self.op_field_mode = op_field_mode
                    self.size_hint_y = None
                    self.height = "35dp"

                def on_release(self):
                    self.op_field_mode.set_value(self.name)
                    self.op_field_mode.close_drop()
                    return super().on_release()

            def __init__(self, op_field_mode: OpScreen.ModeField, **kwargs):
                super().__init__(**kwargs)
                self.op_field_mode = op_field_mode
                self.size_hint = (.75, 1)
                self.mode_button_list = [
                    OpScreen.ModeField.Drop._Button("cb", op_field_mode),
                    OpScreen.ModeField.Drop._Button("cb web", op_field_mode),
                    OpScreen.ModeField.Drop._Button("paypal", op_field_mode),
                    OpScreen.ModeField.Drop._Button("vir", op_field_mode),
                    OpScreen.ModeField.Drop._Button("cash", op_field_mode),
                    OpScreen.ModeField.Drop._Button("cheque", op_field_mode),
                ]
                for mode_button in self.mode_button_list:
                    self.add_widget(mode_button)

        class _Button(Button):

            def __init__(self, op_field_mode: OpScreen.ModeField, **kwargs):
                super().__init__(**kwargs)
                # self.id = "button"
                self.op_field_mode = op_field_mode
                self.size_hint = (.75, 1)
                self.reset_value()
                self.op_field_mode.close_drop()

            def on_release(self, **kwargs):
                self.op_field_mode.open_drop()
                return super().on_release(**kwargs)

            def reset_value(self):
                self.text = self.op_field_mode.drop.mode_button_list[0].text

            def set_value(self, value: str):
                self.text = value

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.id = "mode"
            self.orientation = "horizontal"
            self.add_widget(Label(size_hint=(.25, 1), text="mode"))
            self.drop = OpScreen.ModeField.Drop(self)
            self.add_widget(self.drop)
            self.button = OpScreen.ModeField._Button(self)
            self.add_widget(self.button)

        def reset_value(self):
            self.button.reset_value()

        def set_value(self, value: str):
            self.button.text = value

        def get_value(self):
            return self.button.text

        def open_drop(self):
            self.drop.open(self.button)

        def close_drop(self):
            self.drop.dismiss()

    class _TextInput(TextInput):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.multiline = False
            self.input_type = "text"
            # Seems to be broken at the moment on Swiftkey keyboard
            self.keyboard_suggestions = True
            self.next: Union[OpScreen._TextInput, None] = None

        def on_size(self, *args):
            self.padding = [dp(10), (self.height - self.line_height) / 2]

        def on_text_validate(self):
            if self.next:
                self.next.focus = True
                self.next.select_all()

        def set_next(self, next: OpScreen._TextInput):
            self.next = next

    NAME = "operation"

    def __init__(self, app: BankOpRegisterer, **kwargs):
        super().__init__(**kwargs)

        self.app = app

        self.operation: Operation | None = None

        date_picker = DatePicker()
        today_date_str = date_picker.get_today_date()
        self.today_date_str = f"{today_date_str[6:10]}-{today_date_str[3:5]}-{today_date_str[0:2]}"

        text_input_list: List[OpScreen._TextInput] = []
        for item in self.ids["gridLayout"].children:
            for item_child in item.children:
                if isinstance(item_child, OpScreen._TextInput):
                    text_input_list += [item_child]
        for (text_input_idx, text_input) in enumerate(text_input_list):
            if text_input_idx - 1 >= 0:
                text_input.set_next(text_input_list[text_input_idx - 1])

    def on_enter(self, *args):
        self.set_fields()
        super().on_enter(*args)

    def date_picker_cb(self, date_list):
        """Date picket callback setting label text"""
        date_str = f"{date_list[2]:04d}-{date_list[1]:02d}-{date_list[0]:02d}"
        self.ids["date_label_val"].text = date_str

    def choose_date_btn_cb(self):
        """Date choose button callback"""
        date_picker = DatePicker()
        date_picker.pHint=(0.7, 0.4)
        date_picker.show_popup(None, True, callback=self.date_picker_cb)

    def reset_fields(self):
        """Reset all operation fields"""
        self.ids["date_label_val"].text = self.today_date_str
        self.ids["mode"].reset_value()
        self.ids["tier_input"].text = ""
        self.ids["cat_input"].text = ""
        self.ids["desc_input"].text = ""
        self.ids["amount_input"].text = ""

    def set_fields(self):
        """Set all operations fields"""

        self.reset_fields()

        if not self.operation:
            return

        self.ids["date_label_val"].text = self.operation.date.strftime(Operation.TIME_FMT)
        if self.operation.mode != "":
            self.ids["mode"].set_value(self.operation.mode)
        self.ids["tier_input"].text = self.operation.tier
        self.ids["cat_input"].text = self.operation.category
        self.ids["desc_input"].text = self.operation.description
        self.ids["amount_input"].text = str(self.operation.amount)

    def exit(self):
        """Go back to operations list screen"""
        self.operation = None
        self.app.screen_mgr.current = OpListScreen.NAME

    def cancel_btn_cb(self):
        """Cancel button callback"""
        self.exit()

    def save_btn_cb(self):
        """Save button callback"""

        amount = 0.0
        try:
            amount = float(self.ids["amount_input"].text)
        except ValueError:
            pass

        operation = Operation(
            datetime.strptime(self.ids["date_label_val"].text, Operation.TIME_FMT),
            self.ids["mode"].get_value(),
            self.ids["tier_input"].text,
            self.ids["cat_input"].text,
            self.ids["desc_input"].text,
            amount,
        )

        if self.operation:
            self.app.op_mgr.delete_operation(self.operation)
        self.app.op_mgr.add_operation(operation)
        self.app.op_mgr.save()
        self.exit()

# Aliases for kv file
class OpModeField(OpScreen.ModeField):
    pass
class OpTextInput(OpScreen._TextInput):
    pass

from app import BankOpRegisterer
from internal.operation import Operation
from screens.op_list import OpListScreen
from kivy_calendar.calendar_ui import DatePicker
