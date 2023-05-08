from typing import Callable

import customtkinter as ctk
from tkinter import *
from tkinter import ttk
from PIL import Image

from Utils.constants.constants import *


class TitleFrame(ctk.CTkFrame):
    def __init__(self, master: Tk | ctk.CTk | Frame | ctk.CTkFrame | ttk.LabelFrame,
                 about_open: Callable, tasks_open: Callable, settings_open: Callable,
                 on_close: Callable, **kwargs):
        super(TitleFrame, self).__init__(master=master, **kwargs)
        self.__open_menu_about = about_open
        self.__to_change_size = tasks_open
        self.__open_menu = settings_open
        self.__on_closing = on_close
        self.__cur_path = CURRENT_PATH
        self.__btn_list = []
        self.__build_widget()
        pass

    def __build_widget(self):
        self.__title_image = ctk.CTkImage(Image.open(self.__cur_path.joinpath('social_youtube_2756.ico')), size=(32, 32))
        self.lbl_title_icon = ctk.CTkLabel(self, fg_color='darkblue', height=32, width=32, image=self.__title_image)
        self.lbl_title_icon.bind('<ButtonRelease-1>', self.__open_menu_about)
        self.lbl_title_icon.bind('<ButtonRelease-3>', self.__open_menu_about)
        self.lbl_title_icon.configure(text='', cursor='hand2')
        self.lbl_title_icon.place(y=5, x=10)

        font = ctk.CTkFont(family='Times', size=16, weight='bold')
        self.lbl_title = ctk.CTkLabel(self, fg_color='darkblue', height=32)
        self.lbl_title.configure(text='Youtube media downloader', text_color='white', font=font)
        self.lbl_title.bind('<Enter>', lambda e: self.lbl_title.configure(text_color='lightgreen'))
        self.lbl_title.bind('<Leave>', lambda e: self.lbl_title.configure(text_color='white'))
        self.lbl_title.place(y=5, x=50)

        font = ctk.CTkFont(family='Times', size=14, weight='bold')
        self.btn_title_close_info = ctk.CTkButton(self, text='⏪⏩', text_color='black', font=font, command=self.__to_change_size)
        self.btn_title_close_info.configure(cursor='hand2', hover_color='red', width=30, height=30, fg_color='#3B8ED0')
        self.btn_title_close_info.bind('<Enter>', lambda e: self.btn_title_close_info.configure(text_color='white', fg_color='blue'))
        self.btn_title_close_info.bind('<Leave>', lambda e: self.btn_title_close_info.configure(text_color='black', fg_color='#3B8ED0'))
        self.btn_title_close_info.place(y=5, x=350)

        self.btn_title_settings_icon = ctk.CTkButton(self, text='⚙', text_color='black', font=font)
        self.btn_title_settings_icon.bind('<ButtonRelease-1>', self.__open_menu)
        self.btn_title_settings_icon.bind('<ButtonRelease-3>', self.__open_menu)
        self.btn_title_settings_icon.configure(cursor='hand2', hover_color='red', width=30, height=30, fg_color='#3B8ED0')
        self.btn_title_settings_icon.bind('<Enter>', lambda e: self.btn_title_settings_icon.configure(text_color='white', fg_color='blue'))
        self.btn_title_settings_icon.bind('<Leave>', lambda e: self.btn_title_settings_icon.configure(text_color='black', fg_color='#3B8ED0'))
        self.btn_title_settings_icon.place(y=5, x=410)

        self.btn_close_window = ctk.CTkButton(self, text='❌', fg_color="#3B8ED0")
        self.btn_close_window.configure(cursor='hand2', font=font, command=self.__on_closing)
        self.btn_close_window.configure(hover_color='red', width=30, height=30, text_color='black')
        self.btn_close_window.bind('<Enter>', lambda e: self.btn_close_window.configure(text_color='white', fg_color='red'))
        self.btn_close_window.bind('<Leave>', lambda e: self.btn_close_window.configure(text_color='black', fg_color='#3B8ED0'))
        self.btn_close_window.place(y=5, x=450)

        self.__btn_list = [self.btn_title_close_info, self.btn_title_settings_icon, self.btn_close_window]
        pass

    def buttons_place(self, place_info: list[dict]):
        if place_info and len(place_info) == len(self.__btn_list):
            for i, nxt in enumerate(place_info):
                self.__btn_list[i].place(**nxt)
                pass
        else:
            raise ValueError('Place info is empty or not valid')
        pass

    def title(self, value: str):
        self.lbl_title.configure(text=value)
        pass


    pass