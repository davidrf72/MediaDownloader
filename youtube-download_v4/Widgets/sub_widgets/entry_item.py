from tkinter import *
from typing import Any, Callable
from tkinter.font import Font


class EntryItem(Frame):
    def __init__(self, text_font: tuple, columns_width: int, master: Tk | Frame, **kwargs):
        super(EntryItem, self).__init__(master, **kwargs)
        self.__text_font = text_font
        self.__columns_width = columns_width
        self.__font_measure = Font(font=text_font).measure('e')
        self.__to_minus = 2
        match Font(font=text_font).cget('size'):
            case 8 | 9:
                self.__to_minus = 0
            case 10 | 11 | 12:
                self.__to_minus = 2
            case 13 | 14 | 15 | 16:
                self.__to_minus = 3
            case 17 | 18 | 19 | 20:
                self.__to_minus = 4
            case _:
                self.__to_minus = 7
        self.__build_widget()
        pass

    @property
    def text(self):
        return self.__txt_url.get()
        pass

    @text.setter
    def text(self, value: str):
        self.__txt_url.delete(0, END)
        self.__txt_url.insert(0, str(value))
        pass

    def right_click_bind(self, event_mod: str, callback: Callable):
        self.__txt_url.bind(event_mod, lambda e, txt=self.__txt_url.get(): callback(e, txt))
        pass

    def __build_widget(self):
        self.__txt_url = Entry(self, font=self.__text_font, width=1, highlightthickness=0, relief='flat')
        self.__txt_url.pack(fill=Y, ipadx=(self.__columns_width / 2 - (self.__font_measure-self.__to_minus)))
        pass

    def get(self) -> str:
        return self.__txt_url.get()
        pass

    def insert(self, index: str | int,  string: str) -> None:
        self.__txt_url.insert(index=index, string=string)
        pass

    def delete(self, first: str | int, last: str | int | None = ...):
        self.__txt_url.delete(first, last)
        pass

    def widget_config(self, **kwargs) -> tuple[str, str, str, Any, Any]:
        try:
            bg = kwargs['readonlybackground']
            self.configure(bg=bg)
        except:
            pass
        return self.__txt_url.config(**kwargs)
        pass

    def widget_bind(self, sequence: str, func):
        self.__txt_url.bind(sequence=sequence, func=func)
        pass
    pass
