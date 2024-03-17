"""Operation registerer app main"""

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
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.button import Button
# from kivy.uix.dropdown import DropDown
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
# from kivy.uix.stacklayout import StackLayout
# from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen
# from kivy.uix.textinput import TextInput
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

    def load(self):
        """Load operations list from file"""
        self.op_list.clear()
        with open(f"{expanduser('~')}/{self.file_name}", mode="r", encoding="utf8") as op_list_file:
            op_list_csv_reader = csv.DictReader(op_list_file)
            for op_csv_entry in op_list_csv_reader:
                self.op_list += [Operation.from_csv(op_csv_entry)]

    def add_operation(self, operation: Operation):
        """Add operation"""
        self.op_list += [operation]
        with open(f"{expanduser('~')}/{self.file_name}", mode="a", encoding="utf8") as op_list_file:
            op_list_csv_writer = csv.DictWriter(op_list_file, fieldnames=Operation.CSV_KEY_LIST)
            op_list_csv_writer.writerow(operation.as_csv())

    def save(self):
        """Save operations list to file"""
        with open(f"{expanduser('~')}/{self.file_name}", mode="w", encoding="utf8") as op_list_file:
            op_list_csv_writer = csv.DictWriter(op_list_file, fieldnames=Operation.CSV_KEY_LIST)
            op_list_csv_writer.writeheader()
            for operation in self.op_list:
                op_list_csv_writer.writerow(operation.as_csv())

op_list_mgr = OpListMgr("operation_list.csv")

class AddReceiptScreen(Screen):
    NAME = "add_receipt"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        date_picker = DatePicker()
        date_str = date_picker.get_today_date()
        self.ids["date_label_val"].text = f"{date_str[6:10]}-{date_str[3:5]}-{date_str[0:2]}"

    def date_picker_cb(self, date_list):
        date_str = f"{date_list[2]:04d}-{date_list[1]:02d}-{date_list[0]:02d}"
        self.ids["date_label_val"].text = date_str

    def choose_date_btn(self):
        date_picker = DatePicker()
        date_picker.pHint=(0.7, 0.4)
        date_picker.show_popup(None, True, callback=self.date_picker_cb)

    def clear(self):
        self.ids["mode"].ids["button"].text = self.ids["mode"].ids["cb"].text
        self.ids["tier_input"].text = ""
        self.ids["cat_input"].text = ""
        self.ids["desc_input"].text = ""

    def exit(self):
        self.clear()
        screen_mgr.current = ReceiptListScreen.NAME

    def cancel_btn(self):
        self.exit()

    def add_btn(self):

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
        op_list_mgr.add_operation(operation)
        self.exit()

class ReceiptListScreen(Screen):
    NAME = "receipt_list"

    def on_enter(self, *args):

        op_list_layout = self.ids["op_list_layout"]
        op_list_layout.clear_widgets()
        op_list_layout.height = 0

        op_list_mgr.load()
        for operation in op_list_mgr.op_list:
            receipt_label = Label(text=str(operation))
            receipt_label.size_hint = (1, None)
            receipt_label.size = (100, 30)
            receipt_label.halign = "left"
            op_list_layout.add_widget(receipt_label)
            op_list_layout.height += receipt_label.height

    def add_btn(self):
        screen_mgr.current = AddReceiptScreen.NAME

Window.size = (500, 700)

root_widget = Builder.load_file("main.kv")

screen_mgr = ScreenManager()

screen_list = [ReceiptListScreen(name=ReceiptListScreen.NAME), AddReceiptScreen(name=AddReceiptScreen.NAME)]
for screen in screen_list:
    screen_mgr.add_widget(screen)

screen_mgr.current = ReceiptListScreen.NAME

class BankReceiptRegisterer(App):
    def build(self):
        return screen_mgr

if __name__ == "__main__":
    BankReceiptRegisterer().run()
