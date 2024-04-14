"""Bank operation registerer app main"""

from __future__ import annotations

import configparser
import csv
from dataclasses import dataclass
from datetime import datetime
# from enum import Enum
import logging
# from os.path import expanduser, dirname, join
import os
from os.path import expanduser
# from typing import Any
from typing import List, Union

import kivy
from kivy.app import App
# from kivy.app import App, user_data_dir
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
from kivy.lang import Builder
# from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.layout import Layout
# from kivy.uix.stacklayout import StackLayout
# from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.utils import platform

from kivy_calendar.calendar_ui import DatePicker

from internal.op_mgr import OpMgr
from internal.operation import Operation
from lang_dict import LangDict

if platform == 'android':
    import android
    from android.permissions import Permission, request_permissions, check_permission
    from android.storage import app_storage_path, primary_external_storage_path, secondary_external_storage_path

KEY_ESC = 27

kivy.require('2.3.0')

class OpScreen(Screen):
    """Operation screen"""

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

        self.app = app

        super().__init__(**kwargs)
        self.name = self.NAME

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

    def update_debug(self, widget, value):
        _ = value
        widget.debug_line.rectangle = (widget.x, widget.y, widget.width, widget.height)

    def add_debug(self, widget: Widget):

        if (isinstance(widget, Layout)
            or isinstance(widget, Label)
            or isinstance(widget, Button)):

            if widget.canvas:
                with widget.canvas.before:
                    Color(1, 0, 0, 1)
                    widget.debug_line = ( # pyright: ignore[reportAttributeAccessIssue]
                        Line(width=1, rectangle=(widget.x, widget.y, widget.width, widget.height)))
            widget.bind( # pyright: ignore[reportAttributeAccessIssue]
                pos=self.update_debug, size=self.update_debug)

        for widget_child in widget.children:
            self.add_debug(widget_child)

    def on_enter(self, *args):
        self.set_fields()
        super().on_enter(*args)
        if self.app.get_debug():
            for widget in self.children:
                self.add_debug(widget)

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
        self.app.screen_mgr.transition.direction = "right"
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

class OpEditButton(Button):
    """Operation edit button"""

    def __init__(self, app: BankOpRegisterer, operation: Operation, **kwargs):
        self.app = app
        super().__init__(**kwargs)
        self.operation = operation

    def on_release(self):
        self.app.op_screen.operation = self.operation
        self.app.screen_mgr.transition.direction = "left"
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
        self.app = app
        super().__init__(**kwargs)
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
        self.add_widget(OpEditButton(app, operation, text=app.dict.get("edit"), size_hint=(0.2, 1)))
        self.add_widget(OpDeleteButton(app, operation, text="x", size_hint=(0.1, 1)))

class OpListScreen(Screen):
    """Operations list screen"""

    NAME = "operation_list"

    def __init__(self, app: BankOpRegisterer, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.app = app
        super().__init__(**kwargs)
        self.name = self.NAME

    def update_debug(self, widget, value):
        _ = value
        widget.debug_line.rectangle = (widget.x, widget.y, widget.width, widget.height)

    def add_debug(self, widget: Widget):

        if (isinstance(widget, Layout)
            or isinstance(widget, Label)
            or isinstance(widget, Button)):

            if widget.canvas:
                with widget.canvas.before:
                    Color(1, 0, 0, 1)
                    widget.debug_line = ( # pyright: ignore[reportAttributeAccessIssue]
                        Line(width=1, rectangle=(widget.x, widget.y, widget.width, widget.height)))
            widget.bind( # pyright: ignore[reportAttributeAccessIssue]
                pos=self.update_debug, size=self.update_debug)

        for widget_child in widget.children:
            self.add_debug(widget_child)

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

        if self.app.get_debug():
            for widget in self.children:
                self.add_debug(widget)

    def on_enter(self, *args):
        self.reload()
        super().on_enter(*args)

    def add_btn_cb(self):
        """Add button callback"""
        self.app.screen_mgr.transition.direction = "left"
        self.app.screen_mgr.current = OpScreen.NAME

    def settings_btn_cb(self):
        self.app.screen_mgr.transition.direction = "right"
        self.app.screen_mgr.current = SettingsScreen.NAME

class Settings():

    DICT_DFLT = {
        "main": {
            "lang": "en",
            "debug": "off",
        },
    }

    def __init__(self, file_path: str) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.file_path = file_path
        self.conf_parser = configparser.ConfigParser()
        self.conf_parser.read_dict(self.DICT_DFLT)
        self.load()

    def get(self, option: str, section: str = "main"):
        if not self.conf_parser.has_section(section):
            self.logger.warn("Settings: No section %s", section)
            return ""
        if not self.conf_parser.has_option(section, option):
            self.logger.warn("Settings: No option %s", option)
            return ""
        return self.conf_parser.get(section, option)

    def set(self, option: str, value: str, section: str = "main"):
        self.logger.debug("Settings: set %s = %s", option, value)
        if not self.conf_parser.has_section(section):
            self.conf_parser.add_section(section)
        return self.conf_parser.set(section, option, value)

    def load(self):
        self.logger.debug("Settings: load")
        self.conf_parser.read(self.file_path)

    def save(self):
        self.logger.debug("Settings: save")
        with open(self.file_path, "w") as conf_file:
            self.conf_parser.write(conf_file)

class SettingsScreen(Screen):

    class LanguageField(BoxLayout):

        class Drop(DropDown):

            class _Button(Button):

                def __init__(self, name: str, lang_field: SettingsScreen.LanguageField, **kwargs):
                    super().__init__(text=name, **kwargs)
                    self.id = name
                    self.name = name
                    self.lang_field = lang_field
                    self.size_hint_y = None
                    self.height = "35dp"

                def on_release(self):
                    self.lang_field.set_value(self.name)
                    self.lang_field.close_drop()
                    return super().on_release()

            def __init__(self, lang_field: SettingsScreen.LanguageField, **kwargs):
                super().__init__(**kwargs)
                self.lang_field = lang_field
                self.size_hint = (.75, 1)
                self.mode_button_list = [
                    SettingsScreen.LanguageField.Drop._Button("english", lang_field),
                    SettingsScreen.LanguageField.Drop._Button("francais", lang_field),
                ]
                for mode_button in self.mode_button_list:
                    self.add_widget(mode_button)

        class _Button(Button):

            def __init__(self, lang_field: SettingsScreen.LanguageField, **kwargs):
                super().__init__(**kwargs)
                # self.id = "button"
                self.lang_field = lang_field
                self.size_hint = (.75, 1)
                self.reset_value()
                self.lang_field.close_drop()

            def on_release(self, **kwargs):
                self.lang_field.open_drop()
                return super().on_release(**kwargs)

            def reset_value(self):
                self.text = self.lang_field.drop.mode_button_list[0].text

            def set_value(self, value: str):
                self.text = value

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.id = "mode"
            self.orientation = "horizontal"
            self.add_widget(Label(size_hint=(.25, 1), text="mode"))
            self.drop = SettingsScreen.LanguageField.Drop(self)
            self.add_widget(self.drop)
            self.button = SettingsScreen.LanguageField._Button(self)
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

    NAME = "settings"

    def __init__(self, app: BankOpRegisterer, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.app = app
        super().__init__(**kwargs)
        self.name = self.NAME

    def update_debug(self, widget, value):
        _ = value
        widget.debug_line.rectangle = (widget.x, widget.y, widget.width, widget.height)

    def add_debug(self, widget: Widget):

        if (isinstance(widget, Layout)
            or isinstance(widget, Label)
            or isinstance(widget, Button)):

            if widget.canvas:
                with widget.canvas.before:
                    Color(1, 0, 0, 1)
                    widget.debug_line = ( # pyright: ignore[reportAttributeAccessIssue]
                        Line(width=1, rectangle=(widget.x, widget.y, widget.width, widget.height)))
            widget.bind( # pyright: ignore[reportAttributeAccessIssue]
                pos=self.update_debug, size=self.update_debug)

        for widget_child in widget.children:
            self.add_debug(widget_child)

    def reload(self):
        self.ids["lang"].set_value(self.app.dict.LANG_DICT[self.app.settings.get("lang")])
        self.ids["debug_check"].active = False
        if self.app.settings.get("debug") == "on":
            self.ids["debug_check"].active = True

        if self.app.get_debug():
            for widget in self.children:
                self.add_debug(widget)

    def on_enter(self, *args):
        self.reload()
        super().on_enter(*args)

    def exit(self):
        self.app.screen_mgr.transition.direction = "left"
        self.app.screen_mgr.current = OpListScreen.NAME

    def cancel_btn_cb(self):
        self.exit()

    def save_btn_cb(self):

        settings_changed = False

        lang_name_usr = self.ids["lang"].get_value()
        for (lang_key, lang_name) in self.app.dict.LANG_DICT.items():
            if lang_name == lang_name_usr:
                if self.app.settings.get("lang") != lang_key:
                    self.app.settings.set("lang", lang_key)
                    settings_changed = True
                break

        if self.ids["debug_check"].active:
            if self.app.settings.get("debug") == "off":
                self.app.settings.set("debug", "on")
                settings_changed = True
        else:
            if self.app.settings.get("debug") == "on":
                self.app.settings.set("debug", "off")
                settings_changed = True

        if settings_changed:
            self.app.settings.save()
            self.app.reload()
        else:
            self.logger.debug("SettingsScreen: No change")

        self.exit()

root_widget = Builder.load_file("main.kv")
Window.clearcolor = (0.20, 0.20, 0.20, 1)

class BankOpRegisterer(App):
    """Bank operation registerer app"""

    BASE_DIR_NAME = "bank_op_reg"
    SETTINGS_FILE_NAME = "settings.ini"
    OP_LIST_FILE_NAME = "operation_list.csv"

    def __init__(self, **kwargs):

        self.logger = logging.getLogger(self.__class__.__name__)

        super().__init__(**kwargs)

        if platform == 'android':
            root_dir_path = primary_external_storage_path()
        else:
            root_dir_path = expanduser('~')
        self.logger.debug("BankOpRegisterer: root_dir_path = %s", root_dir_path)

        base_dir_path = f"{root_dir_path}/{self.BASE_DIR_NAME}"
        self.logger.debug("BankOpRegisterer: base_dir_path = %s", base_dir_path)

        if not os.path.isdir(base_dir_path):
            self.logger.debug("BankOpRegisterer: create base_dir_path")
            os.mkdir(base_dir_path)

        self.settings = Settings(f"{base_dir_path}/{self.SETTINGS_FILE_NAME}")

        self.op_mgr = OpMgr(f"{base_dir_path}/{self.OP_LIST_FILE_NAME}")

        self.screen_mgr = ScreenManager()

        self.reload()

        Window.bind(on_keyboard=self.keyboard_cb)

    def keyboard_cb(self, window, key, *largs):
        if key == KEY_ESC:
            if self.screen_mgr.current == OpScreen.NAME:
                self.op_screen.exit()
                return True
            elif self.screen_mgr.current == SettingsScreen.NAME:
                self.settings_screen.exit()
                return True

    def build(self):
        return self.screen_mgr

    def reload(self):
        self.logger.debug("BankOpRegisterer: reload")

        self.dict = LangDict(self.settings.get("lang"))

        self.screen_mgr.clear_widgets()

        self.op_list_screen = OpListScreen(self)
        self.op_screen = OpScreen(self)
        self.settings_screen = SettingsScreen(self)

        screen_list = [
            self.op_list_screen,
            self.op_screen,
            self.settings_screen,
        ]

        for screen in screen_list:
            self.screen_mgr.add_widget(screen)

        self.screen_mgr.current = OpListScreen.NAME

    def get_debug(self):
        if self.settings.get("debug") == "on":
            return True
        return False

def main():
    """Main"""
    logging.basicConfig(level=logging.DEBUG)
    bank_op_register = BankOpRegisterer()
    bank_op_register.run()

def check_permissions(perm_list):
    """Check permissions list"""
    for perm in perm_list:
        if not check_permission(perm):
            return False
    return True

if __name__ == "__main__":
    if platform == 'android':
        perms = [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]
        if not check_permissions(perms):
            request_permissions(perms)
            exit()
    main()
