from tkinter import *
from tkinter import ttk
import customtkinter as ctk
from Widgets.sub_widgets.header_item import HeaderItem



class ScrolledItemHeader(ctk.CTkFrame):
    def __init__(self, master: Misc | None = ..., header_colors: tuple = None, header_font: tuple = None,
                 index: int = 0, **kwargs):
        super(ScrolledItemHeader, self).__init__(master=master, **kwargs)
        self.__index = index
        self.__headers_list = []
        self.__config_header = header_colors if header_colors and len(header_colors) > 0 else ('darkblue', 'blue', 'red', 'lightgreen', 'blue')
        self.__fg_color = self.__config_header[1]
        self.__header_color = self.__config_header[0]
        self.__header_text_color = self.__config_header[3]
        self.__header_hover_color = self.__config_header[2]
        self.__header_hover_text_color = self.__config_header[4]
        self.__header_font = header_font if header_font else ('Ariel', 20, 'bold')
        self.__columns_width = []
        self.__headers_text = []
        pass

    def headers(self, columns_width: list[int], headers_text: list[str]):
        if len(self.__headers_list) > 0:
            for i, nxt_item in enumerate(self.__headers_list):
                nxt_item.pack_forget()
            self.__headers_list.clear()
            self.__frm_title.pack_forget()
        self.__columns_width = columns_width
        self.__headers_text = headers_text
        if len(self.__columns_width) == 0 or len(self.__headers_text) == 0:
            raise ValueError('Invalid data list length')
        if len(self.__columns_width) > len(self.__headers_text):
            addition = len(self.__columns_width) - len(self.__headers_text)
            for _ in range(addition):
                self.__headers_text.append('...')
        if len(self.__columns_width) < len(self.__headers_text):
            addition = len(self.__headers_text) - len(self.__columns_width)
            for _ in range(addition):
                self.__columns_width.append(200)
        self.__build_widget()
        pass

    def __build_widget(self):
        self.__frm_title = ctk.CTkFrame(self, fg_color=self.__fg_color, corner_radius=0)

        for i, nxt_item in enumerate(self.__headers_text):
            self.__headers_list.append(HeaderItem(self.__frm_title, font=self.__header_font, width=self.__columns_width[i], height=50, justify=CENTER))
            self.__headers_list[i].insert(0, nxt_item)
            self.__headers_list[i].configure(state='readonly', corner_radius=10, fg_color=self.__header_color, text_color=self.__header_text_color)
            self.__headers_list[i].bind('<Enter>', lambda e, index=i: self.__config_style_enter(e, index))
            self.__headers_list[i].bind('<Leave>', lambda e, index=i: self.__config_style_leave(e, index))
            self.__headers_list[i].pack(fill=Y, side=LEFT, padx=(4, 2))

        self.__frm_title.pack(fill=BOTH, expand=True, side=TOP)
        pass

    def heading(self, index: int, text='', command=None, image_on=False):
        if 0 > index > (len(self.__headers_list) - 1):
            raise IndexError('Index out of range')
            pass
        if text:
            self.__headers_list[index].configure(text=text)
        if command:
            self.__headers_list[index].configure(command=command)
        if image_on:
            for nxt in self.__headers_list:
                nxt.set_image()
            self.__headers_list[index].set_image(True)
        pass

    def __config_style_enter(self, e, index: int):
        self.__headers_list[index].configure(fg_color=self.__header_hover_color, text_color=self.__header_hover_text_color)
        pass

    def __config_style_leave(self, e, index: int):
        self.__headers_list[index].configure(fg_color=self.__header_color, text_color=self.__header_text_color)
        pass
    pass
