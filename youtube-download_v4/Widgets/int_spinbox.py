from typing import Union, Callable
from tkinter import *
import customtkinter


class IntSpinbox(customtkinter.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: int = 1,
                 to: int = 10,
                 from_: int = 0,
                 start: int = 0,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.__step_size = step_size
        self.__to = to
        self.__from_ = from_
        self.__start = start
        self.__command = command

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6,
                                                       height=height-6, command=self.__subtract_button_callback,
                                                       hover_color='red')
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0)
        self.entry.configure(justify=CENTER, font=('Times', 18, 'bold'))
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6,
                                                  height=height-6, command=self.__add_button_callback,
                                                  hover_color='red')
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, str(self.__start))
        self.entry.configure(state='readonly')

    def __add_button_callback(self):
        if self.__command is not None:
            self.__command()
        try:
            if int(self.entry.get()) < self.__to:
                value = int(self.entry.get()) + self.__step_size
                self.entry.configure(state='normal')
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
                self.entry.configure(state='readonly')
        except ValueError:
            return

    def __subtract_button_callback(self):
        if self.__command is not None:
            self.__command()
        try:
            if int(self.entry.get()) > self.__from_:
                value = int(self.entry.get()) - self.__step_size
                self.entry.configure(state='normal')
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
                self.entry.configure(state='readonly')
        except ValueError:
            return

    def get(self) -> Union[int, None]:
        try:
            return int(self.entry.get())
        except ValueError:
            return None

    def set(self, value: int):
        self.entry.configure(state='normal')
        self.entry.delete(0, "end")
        self.entry.insert(0, str(int(value)))
        self.entry.configure(state='readonly')
        pass
