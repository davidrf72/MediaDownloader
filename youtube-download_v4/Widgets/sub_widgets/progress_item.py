import os
from tkinter import *
from tkinter import ttk
from typing import Any, Callable


class ProgressItem(Frame):
    def __init__(self, variable: IntVar | DoubleVar, columns_width: int, maximum: float, master: Tk | Frame, **kwargs):
        super(ProgressItem, self).__init__(master, **kwargs)
        self.__columns_width = columns_width
        self.__variable = variable
        self.__maximum = maximum
        self.__save_destination = ''
        self.__build_widget()
        pass

    @property
    def save_destination(self):
        return self.__save_destination
        pass

    @save_destination.setter
    def save_destination(self, destination: str):
        if isinstance(destination, str) and os.path.exists(destination):
            self.__save_destination = destination
        pass

    def __build_widget(self):
        self.__scl_progress = ttk.Progressbar(self, variable=self.__variable, maximum=self.__maximum)
        self.__scl_progress.configure(length=self.__columns_width)
        self.__scl_progress.pack(fill=X, expand=True)
        pass

    def right_click_bind(self, event_mod: str, callback: Callable):
        self.__scl_progress.bind(event_mod, lambda e, txt=self.__scl_progress['value']: callback(e, txt))
        pass

    def get(self):
        return self.__scl_progress['value']
        pass

    def widget_config(self, **kwargs) -> tuple[str, str, str, Any, Any]:
        return self.__scl_progress.config(**kwargs)
        pass

    def widget_bind(self, sequence: str, func):
        self.__scl_progress.bind(sequence=sequence, func=func)
        pass
    pass
