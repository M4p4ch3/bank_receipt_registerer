
from os.path import expanduser

import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from KivyCalendar import DatePicker

class AddReceiptScreen(Screen):
    NAME = "add_receipt"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.op_date_label = self.ids["op_date_label"]
        date_picker = DatePicker()
        date_str = date_picker.get_today_date()
        self.op_date_label.text = f"{date_str[6:10]}-{date_str[3:5]}-{date_str[0:2]}"

    def date_picker_cb(self, date_list):
        date_str = f"{date_list[2]:04d}-{date_list[1]:02d}-{date_list[0]:02d}"
        self.op_date_label.text = date_str

    def choose_date_btn(self):
        date_picker = DatePicker()
        date_picker.pHint=(0.7, 0.4)
        date_picker.show_popup(None, True, callback=self.date_picker_cb)

    def cancel_btn(self):
        screen_mgr.current = ReceiptListScreen.NAME

    def add_btn(self):
        screen_mgr.current = ReceiptListScreen.NAME

class ReceiptListLayout(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open(f"{expanduser('~')}/receiptList.txt", "r", encoding="utf8") as receipt_list_file:
            receipt_list_data = receipt_list_file.read()
            for receipt_line_data in receipt_list_data.splitlines():
                receipt_label = Label(text=receipt_line_data)
                receipt_label.size_hint = (1, None)
                receipt_label.size = (100, 30)
                receipt_label.halign = "left"
                # box = BoxLayout()
                # box.add_widget(receipt_label)
                self.add_widget(receipt_label)

    def add_widget(self, widget, *args, **kwargs):
        super().add_widget(widget, *args, **kwargs)
        self.height += widget.height

class ReceiptListScreen(Screen):
    NAME = "receipt_list"
    def on_enter(self, *args):
        pass
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
