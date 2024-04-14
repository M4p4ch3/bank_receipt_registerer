
from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label

class DropDownList(BoxLayout):
    class _DropDown(DropDown):
        class _Button(Button):
            def __init__(self, name: str, drop_down_list: DropDownList, **kwargs):
                super().__init__(**kwargs)
                self.text = name
                self.size_hint_y = None
                self.height = "35dp"

                self.name = name
                self.drop_down_list = drop_down_list

            def on_release(self):
                self.drop_down_list.set(self.name)
                self.drop_down_list.close()
                return super().on_release()

        def __init__(self, drop_down_list: DropDownList, **kwargs):
            super().__init__(**kwargs)
            self.size_hint = (.75, 1)

            self.drop_down_list = drop_down_list

            for item in self.drop_down_list.item_list:
                self.add_widget(DropDownList._DropDown._Button(item, self.drop_down_list))

    class _Button(Button):
        def __init__(self, drop_down_list: DropDownList, **kwargs):
            super().__init__(**kwargs)
            self.size_hint = (.75, 1)

            self.drop_down_list = drop_down_list

            self.reset()
            self.drop_down_list.close()

        def on_release(self, **kwargs):
            self.drop_down_list.open()
            return super().on_release(**kwargs)

        def get(self):
            return self.text

        def set(self, value: str):
            self.text = value

        def reset(self):
            self.set("")
            if len(self.drop_down_list.item_list) > 0:
                self.set(self.drop_down_list.item_list[0])

    def __init__(self, item_list: list[str], **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"

        self.item_list = item_list

        self.drop = DropDownList._DropDown(self)
        self.add_widget(self.drop)
        self.button = DropDownList._Button(self)
        self.add_widget(self.button)

    def reset(self):
        self.button.reset()

    def set(self, value: str):
        self.button.set(value)

    def get(self):
        return self.button.get()

    def open(self):
        self.drop.open(self.button)

    def close(self):
        self.drop.dismiss()
