from typing import Callable

import customtkinter as ctk
from tkinter import *
from tkinter import ttk


class LinkListFrame(ctk.CTkFrame):
    def __init__(self, master: Tk | ctk.CTk | Frame | ctk.CTkFrame | ttk.LabelFrame, task_list_callback: Callable,
                 widget_to_state: list, **kwargs):
        super(LinkListFrame, self).__init__(master=master, **kwargs)
        self.__list_var = StringVar()
        self.__list_url_que = []
        self.__temp_url_que = []
        self.__list_var.set(self.__list_url_que)
        self.__task_list_callback = task_list_callback
        self.__widget_to_state = widget_to_state
        self.__build_widget()
        pass

    def __build_widget(self):
        font = ('Times', 18, 'bold')
        self.__frm_main = ctk.CTkFrame(self, bg_color='blue', fg_color='blue', corner_radius=20, border_color='grey', border_width=2)
        self.__frm_main.pack(fill=BOTH, expand=True)

        self.txt_add_link = ctk.CTkEntry(self.__frm_main, font=('Times', 14))
        self.txt_add_link.bind('<Return>', self.__add_to_list)
        self.txt_add_link.place(relx=0.01, rely=0.07, relwidth=0.7, relheight=0.1)
        self.btn_add_link = ctk.CTkButton(self.__frm_main, text='Add', font=font, text_color='black')
        self.btn_add_link.configure(hover_color='red', command=lambda: self.__add_to_list(None))
        self.btn_add_link.place(relx=0.72, rely=0.07, relwidth=0.27, relheight=0.1)

        frm_url_que = ctk.CTkFrame(self.__frm_main, fg_color='blue')
        frm_url_que.place(relx=0.01, rely=0.18, relwidth=0.98, relheight=0.6)
        self.scr_url_que = ctk.CTkScrollbar(frm_url_que, orientation=VERTICAL, button_hover_color='red')
        self.scr_url_que.pack(fill=Y, side=RIGHT)
        self.lst_url_que = Listbox(frm_url_que, font=('Times', 12), listvariable=self.__list_var, yscrollcommand=self.scr_url_que.set)
        self.lst_url_que.bind('<Delete>', self.__delete_item)
        self.scr_url_que.configure(command=self.lst_url_que.yview)
        self.lst_url_que.pack(fill=BOTH, expand=True, side=LEFT)

        frm_buttons = ctk.CTkFrame(self.__frm_main, fg_color='blue')
        frm_buttons.place(relx=0.01, rely=0.8, relwidth=0.98, relheight=0.14)
        frm_buttons.grid_rowconfigure(0, weight=1)
        frm_buttons.grid_columnconfigure(0, weight=1)
        frm_buttons.grid_columnconfigure(1, weight=1)
        self.btn_ok = ctk.CTkButton(frm_buttons, text='O.K.', corner_radius=30, font=font, text_color='black')
        self.btn_ok.configure(hover_color='red', command=self.__ok_hide)
        self.btn_ok.grid(row=0, column=0, sticky='nsew', padx=(0, 2))
        self.btn_cancel = ctk.CTkButton(frm_buttons, text='Cancel', corner_radius=30, font=font, text_color='black')
        self.btn_cancel.configure(hover_color='red', command=self.__close)
        self.btn_cancel.grid(row=0, column=1, sticky='nsew', padx=(2, 0))
        pass

    @property
    def url_list(self):
        return self.__list_url_que
        pass

    def __add_to_list(self, e):
        if self.txt_add_link.get().lower().startswith(r'https://www.youtube.com/') or \
                self.txt_add_link.get().lower().startswith(r'https://www.facebook.com/') or \
                self.txt_add_link.get().lower().startswith(r'https://fb.watch/'):
            if self.txt_add_link.get():
                if self.txt_add_link.get() not in self.__list_url_que:
                    self.__temp_url_que.append(self.txt_add_link.get())
                    self.__list_var.set(self.__temp_url_que)
        self.txt_add_link.delete(0, END)
        pass

    def __delete_item(self, e):
        if self.lst_url_que.curselection():
            self.__temp_url_que.remove(self.lst_url_que.selection_get())
            self.__list_var.set(self.__temp_url_que)
            pass
        pass

    def show(self, place_params: dict):
        self.place(**place_params)
        self.__temp_url_que = [nxt for nxt in self.__list_url_que]
        self.__list_var.set(self.__temp_url_que)
        for widget in self.__widget_to_state:
            if type(widget) is ctk.CTkEntry:
                widget.delete(0, END)
            widget.configure(state='disabled')
        pass

    def __ok_hide(self):
        self.__list_url_que = [nxt for nxt in self.__temp_url_que]
        self.__temp_url_que = []
        self.__task_list_callback(self.__list_url_que.copy())
        for widget in self.__widget_to_state:
            widget.configure(state='normal')
        self.place_forget()
        pass

    def __close(self):
        self.__list_url_que = []
        self.__temp_url_que = []
        self.__list_var.set(self.__list_url_que)
        self.__task_list_callback(self.__list_url_que)
        self.txt_add_link.delete(0, END)
        for widget in self.__widget_to_state:
            widget.configure(state='normal')
        if self.place_info():
            self.place_forget()
        pass

    def hide(self):
        self.__temp_url_que = []
        self.__list_var.set(self.__list_url_que)
        self.__task_list_callback(self.__list_url_que.copy())
        self.txt_add_link.delete(0, END)
        for widget in self.__widget_to_state:
            widget.configure(state='normal')
        self.place_forget()
        pass

    def clear(self):
        self.__close()
        pass

    pass
