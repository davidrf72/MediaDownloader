from tkinter import *
from typing import Any, Callable


class ButtonItem(Frame):
    def __init__(self, master: Tk | Frame, text_font: tuple, columns_width: int, button_text: str = '', command: Callable = None, **kwargs):
        super(ButtonItem, self).__init__(master=master, **kwargs)
        self.__text_font = text_font
        self.__columns_width = columns_width
        self.__command = command
        self.__button_text = button_text
        self.configure(width=self.__columns_width)
        self.__build_widget()
        pass

    def __build_widget(self):
        self.grid_columnconfigure(0, weight=1)
        self.__btn_button = Button(self, font=self.__text_font, text=self.__button_text, anchor=CENTER, command=lambda: self.__command(self.master.master.iid),
                                   overrelief='ridge', activebackground='red', activeforeground='blue')
        self.__btn_button.pack(fill=X, expand=True, padx=15)
        pass

    def __delete_item(self):
        self.master.destroy()
        pass

    def right_click_bind(self, event_mod: str, callback: Callable):
        #self.__btn_button.bind(event_mod, lambda e, txt=self.__btn_button.get(): callback(e, txt))
        pass

    def widget_config(self, **kwargs) -> tuple[str, str, str, Any, Any]:
        return self.__btn_button.configure(**kwargs)
        pass

    def widget_bind(self, sequence: str, func):
        self.__btn_button.bind(sequence=sequence, func=func)
        pass

    pass