from typing import Callable

import customtkinter as ctk
from tkinter import *
from tkinter import ttk


class TaskAddFrame(ctk.CTkFrame):
    def __init__(self, master: Tk | ctk.CTk | Frame | ctk.CTkFrame | ttk.LabelFrame, add_func: Callable, **kwargs):
        super(TaskAddFrame, self).__init__(master=master, **kwargs)
        self.__add_func = add_func
        self.__build_widget()
        pass

    def __build_widget(self):
        font = ctk.CTkFont(family='Times', size=20, slant='italic')
        lbl_source_link = ctk.CTkLabel(self, text='Source link: ...', fg_color='blue', font=font, text_color='lightgreen')
        lbl_source_link.configure(corner_radius=0, anchor='w')
        lbl_source_link.pack(fill=Y, side=LEFT)
        self.lbl_task_count = ctk.CTkLabel(self, text='Task count: ...', fg_color='#3B8ED0', font=('Times', 12, 'bold'), text_color='black')
        self.lbl_task_count.configure(corner_radius=30, anchor='w')
        self.lbl_task_count.bind('<Enter>', lambda e: self.lbl_task_count.configure(text_color='blue', fg_color='red'))
        self.lbl_task_count.bind('<Leave>', lambda e: self.lbl_task_count.configure(text_color='black', fg_color='#3B8ED0'))
        self.lbl_task_count.pack(fill=Y, side=LEFT, padx=(25, 5))
        self.btn_source_link = ctk.CTkButton(self, text='Add list urls', font=('Times', 14, 'bold'), text_color='lightgreen')
        self.btn_source_link.configure(corner_radius=20, hover_color='red', text_color='black', command=self.__add_func)
        self.btn_source_link.bind('<Enter>', lambda e: self.btn_source_link.configure(text_color='blue', fg_color='red'))
        self.btn_source_link.bind('<Leave>', lambda e: self.btn_source_link.configure(text_color='black', fg_color='#3B8ED0'))
        self.btn_source_link.pack(fill=Y, side=LEFT)
        pass

    @property
    def task_count_text(self):
        return self.lbl_task_count['text']
        pass

    @task_count_text.setter
    def task_count_text(self, value: str):
        count = value if int(value) > 0 else '...'
        self.lbl_task_count.configure(text=f'Task count: {count}')
        pass
    pass