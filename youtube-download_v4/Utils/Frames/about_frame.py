from typing import Callable
import webbrowser
import customtkinter as ctk
from tkinter import *
from tkinter import ttk
from PIL import Image
from Utils.constants.constants import *


class AboutFrame(ctk.CTkFrame):
    def __init__(self, master: Tk | ctk.CTk | Frame | ctk.CTkFrame | ttk.LabelFrame, open_menu_about: Callable, **kwargs):
        super(AboutFrame, self).__init__(master=master, **kwargs)
        self.__open_menu_about = open_menu_about
        self.__build_widget()
        pass

    def __build_widget(self):
        font = ctk.CTkFont(family='Times', size=24, weight='bold')
        frm_about_opt = ttk.LabelFrame(self, labelanchor=N, border=1, text='', padding=10)
        frm_about_opt.place(relx=0.03, rely=0.02, relwidth=0.93, relheight=0.95)
        lbl_resolution_opt = ctk.CTkLabel(self, fg_color='darkblue', bg_color='blue', text_color='red', text='About')
        lbl_resolution_opt.configure(corner_radius=30, font=font, height=40)
        lbl_resolution_opt.place(x=25, y=18, relwidth=0.8)

        font = ctk.CTkFont(family='Times', size=18, weight='bold')
        frm_about_info = ttk.LabelFrame(frm_about_opt, labelanchor=NW, border=1, text='Application info', padding=10)
        frm_about_info.place(relx=0.01, y=25, relwidth=0.98, relheight=0.85)

        txt_style = {'fg_color': 'blue', 'font': font, 'height': 40, 'corner_radius': 15, 'border_width': 0,
                     'text_color': 'lightgreen', 'state': 'readonly'}
        txt_about_app_name = ctk.CTkEntry(frm_about_info)
        txt_about_app_name.insert(0, 'Media downloader')
        txt_about_app_name.configure(**txt_style)
        txt_about_app_name.place(relx=0.01, rely=0, relwidth=0.98)

        txt_about_app_ver = ctk.CTkEntry(frm_about_info)
        txt_about_app_ver.insert(0, 'ver: 4.6.2')
        txt_about_app_ver.configure(**txt_style)
        txt_about_app_ver.place(relx=0.43, rely=0.12, relwidth=0.55)

        txt_about_powered = ctk.CTkEntry(frm_about_info)
        txt_about_powered.insert(0, 'Powered by:')
        txt_about_powered.configure(**txt_style)
        txt_about_powered.place(relx=0.43, rely=0.25, relwidth=0.55)

        txt_about_powered_by = ctk.CTkEntry(frm_about_info)
        txt_about_powered_by.insert(0, 'David 2023 Israel')
        txt_about_powered_by.configure(**txt_style)
        txt_about_powered_by.place(relx=0.01, rely=0.38, relwidth=0.98)

        self.__about_image = ctk.CTkImage(Image.open(RESOURCES_32_PATH.joinpath('youtube_96.png')), size=(96, 96))
        lbl_about_image = ctk.CTkLabel(frm_about_info, text='', image=self.__about_image, width=96, height=96, fg_color='blue')
        lbl_about_image.configure(cursor='hand2')
        lbl_about_image.bind('<ButtonRelease-1>', lambda e: webbrowser.open('https://www.youtube.com/'))
        lbl_about_image.place(relx=0.01, rely=0.12)

        frm_menu_about_buttons = ctk.CTkFrame(frm_about_opt, fg_color='blue')
        frm_menu_about_buttons.place(relx=0.25, rely=0.92)
        self.btn_menu_ok = ctk.CTkButton(frm_menu_about_buttons, text='O.K.', command=self.__open_menu_about, **BUTTON_STYLE)
        self.btn_menu_ok.bind('<Enter>', lambda e: self.btn_menu_ok.configure(text_color='blue', fg_color='red'))
        self.btn_menu_ok.bind('<Leave>', lambda e: self.btn_menu_ok.configure(text_color='black', fg_color='#3B8ED0'))
        self.btn_menu_ok.pack()
        pass
    pass
