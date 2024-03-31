"""Bank operation registerer app main"""

from __future__ import annotations

import csv
# from dataclasses import dataclass
from datetime import datetime
# from enum import Enum
import logging
from os.path import expanduser, dirname, join
# from typing import Any
from typing import List

import kivy
from kivy.app import App
# from kivy.app import App, user_data_dir
from kivy.core.window import Window
from kivy.lang import Builder
# from kivy.logger import Logger
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
# from kivy.uix.stacklayout import StackLayout
# from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen
# from kivy.uix.textinput import TextInput
# from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.utils import platform

from kivy_calendar.calendar_ui import DatePicker

if platform == 'android':
    import android
    from android.permissions import Permission, request_permissions, check_permission
    from android.storage import app_storage_path, primary_external_storage_path, secondary_external_storage_path

kivy.require('2.3.0')

class Operation:
    """Operation"""

    CSV_KEY_DATE = "date"
    CSV_KEY_MODE = "mode"
    CSV_KEY_TIER = "tier"
    CSV_KEY_CAT = "category"
    CSV_KEY_DESC = "description"
    CSV_KEY_AMOUNT = "amount"

    CSV_KEY_LIST = [
        CSV_KEY_DATE,
        CSV_KEY_MODE,
        CSV_KEY_TIER,
        CSV_KEY_CAT,
        CSV_KEY_DESC,
        CSV_KEY_AMOUNT,
    ]

    TIME_FMT = "%Y-%m-%d"

    def __init__(self, date: datetime = datetime.now(), mode: str = "", tier: str = "",
        category: str = "", description: str = "", amount: float = 0.0):

        self.date = date
        self.mode = mode
        self.tier = tier
        self.category = category
        self.description = description
        self.amount = amount

    @classmethod
    def from_csv(cls, csv_entry: dict):
        """Create Operation from CSV entry"""
        return Operation(
            datetime.strptime(csv_entry[cls.CSV_KEY_DATE], cls.TIME_FMT),
            csv_entry[cls.CSV_KEY_MODE],
            csv_entry[cls.CSV_KEY_TIER],
            csv_entry[cls.CSV_KEY_CAT],
            csv_entry[cls.CSV_KEY_DESC],
            float(csv_entry[cls.CSV_KEY_AMOUNT]),
        )

    def as_csv(self) -> dict:
        """Get as CSV entry"""
        return {
            self.CSV_KEY_DATE: self.date.strftime(self.TIME_FMT),
            self.CSV_KEY_MODE: self.mode,
            self.CSV_KEY_TIER: self.tier,
            self.CSV_KEY_CAT: self.category,
            self.CSV_KEY_DESC: self.description,
            self.CSV_KEY_AMOUNT: str(self.amount),
        }

    def __str__(self) -> str:
        return (f"{self.date.strftime(self.TIME_FMT)}, {self.mode}, {self.tier}, "
            f"{self.category}, {self.description}, {self.amount}")

class OpListMgr():
    """Operations list manager"""

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.op_list: List[Operation] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.load()

    def add_operation(self, operation: Operation):
        """Add operation"""
        self.logger.debug("OpListMgr: add Operation(%s)", operation)
        self.op_list += [operation]

    def delete_operation(self, operation: Operation):
        """Delete operation"""
        self.logger.debug("OpListMgr: delete Operation(%s)", operation)
        self.op_list.remove(operation)

    def load(self):
        """Load operations list from file"""

        self.logger.debug("OpListMgr: load")
        self.op_list.clear()

        if platform == 'android':
            self.file_dir_path = primary_external_storage_path()
        else:
            self.file_dir_path = expanduser('~')

        print(f"OpListMgr: self.file_name = {self.file_name}")
        self.logger.info("OpListMgr: self.file_name = %s", self.file_name)
        print(f"OpListMgr: self.file_dir_path = {self.file_dir_path}")
        self.logger.info("OpListMgr: self.file_dir_path = %s", self.file_dir_path)

        # Ensure file exists by open in write mode
        with open(f"{self.file_dir_path}/{self.file_name}", mode="a", encoding="utf8"):
            pass

        with open(f"{self.file_dir_path}/{self.file_name}", mode="r", encoding="utf8") as op_list_file:
            op_list_csv_reader = csv.DictReader(op_list_file)
            for op_csv_entry in op_list_csv_reader:
                self.op_list += [Operation.from_csv(op_csv_entry)]

    def save(self):
        """Save operations list to file"""
        self.logger.debug("OpListMgr: save")
        with open(f"{self.file_dir_path}/{self.file_name}", mode="w", encoding="utf8") as op_list_file:
            op_list_csv_writer = csv.DictWriter(op_list_file, fieldnames=Operation.CSV_KEY_LIST)
            op_list_csv_writer.writeheader()
            for operation in self.op_list:
                op_list_csv_writer.writerow(operation.as_csv())

class OperationFieldMode(BoxLayout):

    class Drop(DropDown):

        class _Button(Button):

            def __init__(self, name: str, op_field_mode: OperationFieldMode, **kwargs):
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

        def __init__(self, op_field_mode: OperationFieldMode, **kwargs):
            super().__init__(**kwargs)
            self.op_field_mode = op_field_mode
            self.size_hint = (.75, 1)
            self.mode_button_list = [
                OperationFieldMode.Drop._Button("cb", op_field_mode),
                OperationFieldMode.Drop._Button("cb web", op_field_mode),
                OperationFieldMode.Drop._Button("paypal", op_field_mode),
                OperationFieldMode.Drop._Button("vir", op_field_mode),
                OperationFieldMode.Drop._Button("cash", op_field_mode),
                OperationFieldMode.Drop._Button("cheque", op_field_mode),
            ]
            for mode_button in self.mode_button_list:
                self.add_widget(mode_button)

    class _Button(Button):

        def __init__(self, op_field_mode: OperationFieldMode, **kwargs):
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
        self.drop = OperationFieldMode.Drop(self)
        self.add_widget(self.drop)
        self.button = OperationFieldMode._Button(self)
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

class OperationScreen(Screen):
    """Operation screen"""

    NAME = "operation"

    def __init__(self, app: BankOperationRegisterer, **kwargs):
        super().__init__(**kwargs)

        self.app = app
        self.operation: Operation | None = None

        date_picker = DatePicker()
        today_date_str = date_picker.get_today_date()
        self.today_date_str = f"{today_date_str[6:10]}-{today_date_str[3:5]}-{today_date_str[0:2]}"

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
        if self.operation.amount != 0.0:
            self.ids["amount_input"].text = self.operation.amount

    def exit(self):
        """Go back to operations list screen"""
        self.operation = None
        self.app.screen_mgr.current = OperationListScreen.NAME

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
            self.app.op_list_mgr.delete_operation(self.operation)
        self.app.op_list_mgr.add_operation(operation)
        self.app.op_list_mgr.save()
        self.exit()

class OpEditButton(Button):
    """Operation edit button"""

    def __init__(self, app: BankOperationRegisterer, operation: Operation, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.operation = operation

    def on_release(self):
        self.app.op_screen.operation = self.operation
        self.app.screen_mgr.current = OperationScreen.NAME
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

    def __init__(self, app: BankOperationRegisterer, operation: Operation, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.operation = operation
        self.confirm_popup = ConfirmPopup("Delete operation")
        self.confirm_popup.on_dismiss=self.confirm_popup_dismiss_cb

    def confirm_popup_dismiss_cb(self):
        """Confirmation popup dismiss callback"""
        if self.confirm_popup.status:
            self.app.op_list_mgr.delete_operation(self.operation)
            self.app.op_list_mgr.save()
            self.app.op_list_screen.reload()

    def on_release(self):
        self.confirm_popup.open()
        super().on_release()

class OperationLayout(BoxLayout):
    """Operation layout"""
    def __init__(self, app: BankOperationRegisterer, operation: Operation):
        super().__init__()
        self.orientation = "horizontal"
        self.add_widget(Label(text=str(operation)))
        self.add_widget(OpEditButton(app, operation, text="edit", size_hint=(0.3, 1)))
        self.add_widget(OpDeleteButton(app, operation, text="x", size_hint=(0.15, 1)))

class OperationListScreen(Screen):
    """Operations list screen"""

    NAME = "operation_list"

    def __init__(self, app: BankOperationRegisterer, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.logger = logging.getLogger(self.__class__.__name__)

    def reload(self):
        """Update operations list"""
        self.logger.debug("OperationListScreen: reload")
        op_list_layout = self.ids["op_list_layout"]
        op_list_layout.clear_widgets()
        op_list_layout.height = 0

        for operation in self.app.op_list_mgr.op_list:
            operation_layout = OperationLayout(self.app, operation)
            operation_layout.size_hint = (1, None)
            operation_layout.size = (1, dp(35))
            op_list_layout.add_widget(operation_layout)
            op_list_layout.height += operation_layout.height

    def on_enter(self, *args):
        self.reload()
        super().on_enter(*args)

    def add_btn_cb(self):
        """Add button callback"""
        self.app.screen_mgr.current = OperationScreen.NAME

# Window.size = (500, 700)
# from kivy.config import Config
# Config.set('graphics', 'width', '720')
# Config.set('graphics', 'height', '1280')

root_widget = Builder.load_file("main.kv")

class BankOperationRegisterer(App):
    """Bank operation registerer app"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.op_list_mgr = OpListMgr("operation_list.csv")
        self.screen_mgr = ScreenManager()
        self.op_list_screen = OperationListScreen(self, name=OperationListScreen.NAME)
        self.op_screen = OperationScreen(self, name=OperationScreen.NAME)

        screen_list = [
            self.op_list_screen,
            self.op_screen,
        ]

        for screen in screen_list:
            self.screen_mgr.add_widget(screen)

        self.screen_mgr.current = OperationListScreen.NAME

    def build(self):
        return self.screen_mgr

def main():
    """Main"""
    logging.basicConfig(level=logging.DEBUG)
    bank_op_register = BankOperationRegisterer()
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
