"""Bank operation registerer app main"""

from __future__ import annotations

import csv
# from dataclasses import dataclass
from datetime import datetime
# from enum import Enum
from os.path import expanduser
# from typing import Any
from typing import List

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
# from kivy.uix.dropdown import DropDown
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
# from kivy.uix.stacklayout import StackLayout
# from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen
# from kivy.uix.textinput import TextInput
# from kivy.uix.widget import Widget
from KivyCalendar import DatePicker

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

    def __init__(self, date: datetime, mode: str, tier: str,
        category: str, description: str, amount: float):

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
        self.load()

    def add_operation(self, operation: Operation):
        """Add operation"""
        self.op_list += [operation]
        # with open(f"{expanduser('~')}/{self.file_name}", mode="a", encoding="utf8") as op_list_file:
        #     op_list_csv_writer = csv.DictWriter(op_list_file, fieldnames=Operation.CSV_KEY_LIST)
        #     op_list_csv_writer.writerow(operation.as_csv())

    def delete_operation(self, op_idx: int):
        """Delete operation from index"""
        if op_idx < len(self.op_list):
            self.op_list.pop(op_idx)

    def load(self):
        """Load operations list from file"""
        self.op_list.clear()
        with open(f"{expanduser('~')}/{self.file_name}", mode="r", encoding="utf8") as op_list_file:
            op_list_csv_reader = csv.DictReader(op_list_file)
            for op_csv_entry in op_list_csv_reader:
                self.op_list += [Operation.from_csv(op_csv_entry)]

    def save(self):
        """Save operations list to file"""
        with open(f"{expanduser('~')}/{self.file_name}", mode="w", encoding="utf8") as op_list_file:
            op_list_csv_writer = csv.DictWriter(op_list_file, fieldnames=Operation.CSV_KEY_LIST)
            op_list_csv_writer.writeheader()
            for operation in self.op_list:
                op_list_csv_writer.writerow(operation.as_csv())

class AddOperationScreen(Screen):
    """Add operation screen"""

    NAME = "add_operation"

    def __init__(self, app: BankOperationRegisterer, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        date_picker = DatePicker()
        date_str = date_picker.get_today_date()
        self.ids["date_label_val"].text = f"{date_str[6:10]}-{date_str[3:5]}-{date_str[0:2]}"

    def date_picker_cb(self, date_list):
        """Date picket callback setting label text"""
        date_str = f"{date_list[2]:04d}-{date_list[1]:02d}-{date_list[0]:02d}"
        self.ids["date_label_val"].text = date_str

    def choose_date_btn_cb(self):
        """Date choose button callback"""
        date_picker = DatePicker()
        date_picker.pHint=(0.7, 0.4)
        date_picker.show_popup(None, True, callback=self.date_picker_cb)

    def clear(self):
        """Clear all operation fields"""
        self.ids["mode"].ids["button"].text = self.ids["mode"].ids["cb"].text
        self.ids["tier_input"].text = ""
        self.ids["cat_input"].text = ""
        self.ids["desc_input"].text = ""

    def exit(self):
        """Go back to operations list screen"""
        self.clear()
        self.app.screen_mgr.current = OperationListScreen.NAME

    def cancel_btn_cb(self):
        """Cancel button callback"""
        self.exit()

    def add_btn_cb(self):
        """Add button callback"""

        amount = 0.0
        try:
            amount = float(self.ids["amount_input"].text)
        except ValueError:
            pass

        operation = Operation(
            datetime.strptime(self.ids["date_label_val"].text, Operation.TIME_FMT),
            self.ids["mode"].ids["button"].text,
            self.ids["tier_input"].text,
            self.ids["cat_input"].text,
            self.ids["desc_input"].text,
            amount,
        )

        print(str(operation))
        self.app.op_list_mgr.add_operation(operation)
        self.app.op_list_mgr.save()
        self.exit()

class OpDeleteButton(Button):
    """Operation delete button"""

    def __init__(self, app: BankOperationRegisterer, op_idx: int, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.op_idx = op_idx

    def on_release(self):
        self.app.op_list_mgr.delete_operation(self.op_idx)
        self.app.op_list_mgr.save()
        self.app.op_list_screen.reload()
        return super().on_release()

class OperationLayout(BoxLayout):
    """Operation layout"""
    def __init__(self, app: BankOperationRegisterer, op_idx: int, op_str: str):
        super().__init__()
        self.orientation = "horizontal"
        self.add_widget(Label(text=op_str))
        self.add_widget(OpDeleteButton(app, op_idx, text="x", size_hint=(0.1, 1)))

class OperationListScreen(Screen):
    """Operations list screen"""

    NAME = "operation_list"

    def __init__(self, app: BankOperationRegisterer, **kwargs):
        super().__init__(**kwargs)
        self.app = app

    def reload(self):
        """Update operations list"""
        op_list_layout = self.ids["op_list_layout"]
        op_list_layout.clear_widgets()
        op_list_layout.height = 0

        for (op_idx, operation) in enumerate(self.app.op_list_mgr.op_list):
            operation_layout = OperationLayout(self.app, op_idx, str(operation))
            operation_layout.size_hint = (1, None)
            operation_layout.size = (100, 30)
            op_list_layout.add_widget(operation_layout)
            op_list_layout.height += operation_layout.height

    def on_enter(self, *args):
        self.reload()

    def add_btn_cb(self):
        """Add button callback"""
        self.app.screen_mgr.current = AddOperationScreen.NAME

Window.size = (500, 700)

root_widget = Builder.load_file("main.kv")

class BankOperationRegisterer(App):
    """Bank operation registerer app"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.op_list_mgr = OpListMgr("operation_list.csv")
        self.screen_mgr = ScreenManager()
        self.op_list_screen = OperationListScreen(self, name=OperationListScreen.NAME)

        screen_list = [
            self.op_list_screen,
            AddOperationScreen(self, name=AddOperationScreen.NAME)
        ]

        for screen in screen_list:
            self.screen_mgr.add_widget(screen)

        self.screen_mgr.current = OperationListScreen.NAME

    def build(self):
        return self.screen_mgr

def main():
    """Main"""
    bank_op_register = BankOperationRegisterer()
    bank_op_register.run()

if __name__ == "__main__":
    main()
