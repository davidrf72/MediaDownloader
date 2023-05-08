import os
from tkinter import *
from tkinter import ttk, messagebox
from typing import Callable, Any, Literal
import webbrowser
from Widgets.sub_widgets.entry_item import EntryItem
from Widgets.sub_widgets.progress_item import ProgressItem
from Widgets.sub_widgets.button_item import ButtonItem


class ScrolledFrameItem(Frame):
    def __init__(self, master: Misc | None = ..., row_colors: tuple = None, text_font: tuple = None, index: int = 0,
                 values: list = None, columns_width: list[int] = None, selection_callback: Callable = None,
                 row_collback: Callable = None, delete_callback: Callable = None,
                 **kwargs):
        """Row widgets container

        :param master: Parent container
        :param row_colors: Row color style
        :param text_font: Row text font
        :param index: Row index
        :param values: List of values
        :param columns_width: Cells width
        :param selection_callback: Callback to get selected row values
        :param row_collback: Callback to get rows values by mouse Enter and Leave events
        :param kwargs: tkinter.Frame options
        """
        super(ScrolledFrameItem, self).__init__(master=master, **kwargs)
        self.__index = index
        self.__iid = f'#{index}'
        self.__values = values
        self.__selected_column = -1
        self.__selection_callback = selection_callback
        self.__row_callback_func = row_collback
        self.__delete_callback = delete_callback
        self.__config_row = row_colors if row_colors and len(row_colors) > 0 else ('white', 'silver', 'silver', 'blue')
        self.__cell_color = self.__config_row[0]
        self.__active_cell_color = self.__config_row[1]
        self.__row_color = self.__config_row[2]
        self.__active_row_color = self.__config_row[3]
        self.__text_font = text_font if text_font else ('Times', 14)
        self.__columns_width = columns_width  # if columns_width else [300, 220, 200]
        self.__entries_items_list = []
        self.__save_destination = ''
        self.configure(bg=self.__row_color)
        self.__exception_value = None
        self.__build_widget()
        pass

    @property
    def exception_value(self) -> tuple:
        return self.__exception_value
        pass

    @exception_value.setter
    def exception_value(self, value: tuple):
        self.__exception_value = value
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

    @property
    def iid(self) -> str:
        return self.__iid

    @property
    def progress(self) -> float:
        return self.__scl_progress_var.get()

    @progress.setter
    def progress(self, value: float):
        self.__values[1] = value
        self.__scl_progress_var.set(value=value)
        pass

    @property
    def url(self):
        return self.__values[0]
        pass

    @url.setter
    def url(self, value: str):
        if value:
            self.__frm_url.widget_config(state='normal')
            self.__frm_url.delete(0, END)
            self.__frm_url.insert(0, value)
            self.__frm_url.widget_config(state='readonly')
        pass

    @property
    def file_count_info(self) -> list:
        return self.__values[2]
        pass

    @file_count_info.setter
    def file_count_info(self, value: tuple | str):
        if value:
            txt = ''
            if isinstance(value, tuple):
                txt = f'File Nº: {value[0]} from: {value[1]}'
            elif isinstance(value, str):
                txt = value
            self.__values[2] = value
            self.__frm_txt_file_count.widget_config(state='normal')
            self.__frm_txt_file_count.delete(0, END)
            self.__frm_txt_file_count.insert(0, txt)
            self.__frm_txt_file_count.widget_config(state='readonly')
        pass

    def button_config(self, **kwargs):
        self.__frm_button.widget_config(**kwargs)
        pass

    def __build_widget(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Horizontal.TProgressbar", foreground='red', background='red', troughcolor=self.__cell_color, darkcolor='blue', lightcolor='blue')
        self.style.configure("selected.Horizontal.TProgressbar", troughcolor=self.__active_cell_color, bordercolor=self.__active_row_color)

        self.__frm_main = Frame(self, bg=self.__row_color)
        self.__frm_main.pack(fill=BOTH, expand=True, pady=1)

        self.__frm_url = EntryItem(master=self.__frm_main, text_font=self.__text_font, columns_width=self.__columns_width[0])
        self.__frm_url.insert(0, f'{self.__values[0]}')  # - {self.__index}')
        self.__frm_url.widget_bind('<Button-1>', lambda e: self.__button_pressed(e))
        #self.__frm_url.widget_bind('<Double-Button-1>', lambda e: webbrowser.open(self.__frm_url.text))
        self.__frm_url.widget_bind('<Double-Button-1>', lambda e: self.__double_click(action='url', destination=self.__frm_url.text))
        self.__frm_url.widget_config(state='readonly', readonlybackground=self.__cell_color)
        self.__frm_url.pack(fill=BOTH, side=LEFT, padx=(4, 2))
        self.__entries_items_list.append(self.__frm_url)

        self.__scl_progress_var = DoubleVar(value=float(self.__values[1]))
        self.__frm_scl_progress = ProgressItem(master=self.__frm_main, variable=self.__scl_progress_var, columns_width=self.__columns_width[1], maximum=1)
        self.__frm_scl_progress.widget_bind('<Button-1>', lambda e: self.__button_pressed(e))
        #self.__frm_scl_progress.widget_bind('<Double-Button-1>', lambda e: os.startfile(self.save_destination))
        self.__frm_scl_progress.widget_bind('<Double-Button-1>', lambda e: self.__double_click(action='folder', destination=self.save_destination))
        self.__frm_scl_progress.widget_config(length=self.__columns_width[1])
        self.__frm_scl_progress.pack(fill=BOTH, side=LEFT, padx=(2, 2))
        self.__entries_items_list.append(self.__frm_scl_progress)

        self.__frm_txt_file_count = EntryItem(master=self.__frm_main, text_font=self.__text_font, columns_width=self.__columns_width[2])
        val = 'Waiting...' #'File Nº: ? from ??'
        self.__frm_txt_file_count.insert(0, val)
        self.__frm_txt_file_count.widget_bind('<Button-1>', lambda e: self.__button_pressed(e))
        #self.__frm_txt_file_count.widget_bind('<Double-Button-1>', lambda e: os.startfile(self.save_destination))
        self.__frm_txt_file_count.widget_bind('<Double-Button-1>', lambda e: self.__double_click(action='folder', destination=self.save_destination))
        self.__frm_txt_file_count.widget_config(state='readonly', readonlybackground=self.__cell_color)
        self.__frm_txt_file_count.pack(fill=BOTH, side=LEFT, padx=(2, 2))
        self.__entries_items_list.append(self.__frm_txt_file_count)

        val = f'Delete item: {self.__index+1}'
        self.__frm_button = ButtonItem(master=self.__frm_main, text_font=self.__text_font, button_text=val,
                                       columns_width=self.__columns_width[3], bg=self.__row_color,
                                       command=self.__delete_callback)
        self.__frm_button.widget_bind('<Button-1>', lambda e: self.__button_pressed(e))
        self.__frm_button.widget_config(bg=self.__cell_color)
        self.__frm_button.pack(fill=BOTH, expand=True, side=LEFT, padx=(2, 4))
        self.__entries_items_list.append(self.__frm_button)

        if self.__row_callback_func:
            for i in range(len(self.__entries_items_list)):
                self.__entries_items_list[i].bind('<Enter>', lambda e: self.__row_callback(e, 'Enter'))
                self.__entries_items_list[i].bind('<Leave>', lambda e: self.__row_callback(e, 'Leave'))
        pass

    def __double_click(self, action: Literal['url', 'folder'], destination: str) -> None:
        """Sets action on widget doubleclick event: open save destination path or url

        :param action: What function will do: 'folder' - open save path, 'url' - open video url
        :param destination: Video save folder path or url
        :return: None
        """
        if self.exception_value:
            tmp = ''
            msg = 'Those files are missing:\n' if len(self.exception_value[2]) > 1 else 'This file is missing\n'
            for i, nxt_file in enumerate(self.exception_value[2]):
                separate = '\n' if len(self.exception_value[2]) - 1 > i else ''
                tmp += f'{nxt_file}{separate}'
                pass
            message = f'There is an error has occurred: "{self.exception_value[0]}"\n\n{msg}{tmp}'
            print(self.exception_value)
            title = 'files' if len(self.exception_value[2]) > 1 else 'file'
            messagebox.showerror(title=f'Error Message: missing {self.exception_value[1]} {title}', message=message, parent=self.winfo_toplevel())
        match action:
            case 'url':
                webbrowser.open(destination)
                pass
            case 'folder':
                if os.path.exists(destination):
                    os.startfile(destination)
                pass
        pass

    def __row_callback(self, e, state: str) -> None:
        """Callback function witch works with Enter and Leave events

        :param e: Event object
        :param state: Enter or leave event occurred
        :return: None
        """
        column = -1
        widgets_width = 0
        if type(e.widget) is EntryItem:
            x_pos = e.widget.winfo_x()
        elif type(e.widget) is ProgressItem:
            x_pos = e.widget.winfo_x()
        elif type(e.widget) is ButtonItem:
            x_pos = e.widget.winfo_x()
        else:
            x_pos = e.x
        for i, nxt in enumerate(self.__entries_items_list):
            widgets_width += nxt.winfo_reqwidth()
            if x_pos < widgets_width:
                column = i
                break
        if column == -1:
            return
        if state == 'Enter':
            self.__row_callback_func(e, (self.__iid, self.__values, self, column))
            return
        self.__row_callback_func(e, ())
        pass

    def __button_pressed(self, e):
        column = -1
        for i, nxt in enumerate(self.__frm_main.winfo_children()):
            if e.widget is nxt.winfo_children()[0]:
                column = i
        if column == -1:
            raise ValueError('No such column in widget')
        if self.__selection_callback:
            self.__selected_column = column
            self.__selection_callback((self.__iid, self.__values[column], self.__values, self, column))
        pass

    def get_value(self):
        return self.__iid, self.__values[0], self.__values, self, 0
        pass

    def right_click_bind(self, event_mod: str, callback: Callable):
        def item_callback(e, entry_value: str):
            entry_index = -1
            for i, nxt in enumerate(self.__entries_items_list):
                if e.widget.master is nxt:
                    entry_index = i
                    break
            values = []
            for nxt in self.__entries_items_list:
                if type(nxt) is EntryItem:
                    values.append(nxt.get())
                elif type(nxt) is ProgressItem:
                    values.append(nxt.get())
            callback(e, (self.__iid, entry_index, entry_value, values))
            self.__button_pressed(e)
            pass

        for nxt in self.__entries_items_list:
            nxt.right_click_bind(event_mod, item_callback)
        pass

    def config_selection(self, activate=True):
        self.__frm_main.configure(bg=self.__active_row_color if activate else self.__row_color)
        self.__select_column(activate)
        pass

    def __select_column(self, activate=True):
        self.configure(bg=self.__row_color if not activate else self.__active_row_color)
        self.__frm_url.widget_config(readonlybackground=self.__cell_color)
        self.__frm_scl_progress.widget_config(style="Horizontal.TProgressbar")
        self.__frm_txt_file_count.widget_config(readonlybackground=self.__cell_color)
        self.__frm_button.widget_config(bg=self.__cell_color)
        #self.__frm_button.configure(bg=self.__active_row_color if activate else self.__row_color)
        match self.__selected_column:
            case 0:
                self.__frm_url.widget_config(readonlybackground=self.__active_cell_color if activate else self.__cell_color)
            case 1:
                self.__frm_scl_progress.widget_config(style="Horizontal.TProgressbar" if not activate else "selected.Horizontal.TProgressbar")
            case 2:
                self.__frm_txt_file_count.widget_config(readonlybackground=self.__active_cell_color if activate else self.__cell_color)
            case 3:
                self.__frm_button.widget_config(bg=self.__active_cell_color if activate else self.__cell_color)
        pass
    pass
