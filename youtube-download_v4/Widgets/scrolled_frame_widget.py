import sys
from tkinter import *
from typing import Callable

from .scrolled_frame_item2_tk_dinamic import ScrolledFrameItem
from .scrolled_item_header import ScrolledItemHeader
import customtkinter as ctk
from datetime import datetime as dt
import functools
fp = functools.partial

class ScrolledFrame(ctk.CTkFrame):
    def __init__(self, headers_text: list[str], master: Misc | None = ..., columns_width: list[int] = None,
                 field_color: str = None, scroll_button_colors: tuple = None, header_colors: tuple = None,
                 row_colors: tuple = None, header_font: tuple = None, text_font: tuple = None,
                 row_callback: Callable = None, **kwargs):
        """Like ttk.TreeView widget

        :param master: Parent window or frame
        :param field_color: Field color of widget
        :param scroll_button_colors: ('Background', 'Button', 'Hover') colors of scroll bars
        :param header_colors: ('Labels', 'Background', 'Label hover', 'Text', 'Active text') colors of widget header
        :param row_colors: ('Cell', 'Selected cell', 'Row', 'Selected row') colors of widget row items
        :param header_font: Header font
        :param text_font: Text font of widget rows text
        :param columns_width: List of columns width values
        :param row_callback allow transfer row data by mouse over events
        :param kwargs:
        """
        super(ScrolledFrame, self).__init__(master=master, **kwargs)
        if len(headers_text) == 0:
            raise ValueError('Invalid headers list length')
        self.__width = 0
        self.__height = 0
        self.__items = []
        self.__count = 0
        self.__selection = ()
        self.__fild_color = field_color if field_color else 'white'
        self.__scroll_button_colors = scroll_button_colors if scroll_button_colors and len(
            scroll_button_colors) > 0 else ('silver', 'gray', 'red')
        self.__scroll_button_style = {'fg_color': self.__scroll_button_colors[0],
                                      'button_color': self.__scroll_button_colors[1],
                                      'button_hover_color': self.__scroll_button_colors[2]}
        self.__config_header = header_colors if header_colors and len(header_colors) > 0 else (
        'gray', 'silver', 'red', 'black', 'blue')
        self.__config_row = row_colors if row_colors and len(row_colors) > 0 else ('white', 'silver', 'silver', 'blue')
        self.__header_font = header_font if header_font else ('Ariel', 20, 'bold')
        self.__text_font = text_font if text_font else ('Ariel', 12, 'italic')
        self.__columns_width = columns_width if columns_width else [200 for _ in range(len(headers_text))]
        self.__headers_text = headers_text
        self.__row_callback_func = row_callback
        self.move_to = 10
        self.__build_widget()
        pass

    def __build_widget(self):
        self.__frm_main_out = Frame(self)

        self.canvas_window = Canvas(self.__frm_main_out, bg=self.__fild_color, highlightthickness=0)
        self.__frm_main_in = ctk.CTkFrame(self.canvas_window)
        self.__frm_title = ScrolledItemHeader(self.__frm_main_in, height=50, header_colors=self.__config_header, header_font=self.__header_font)
        self.__frm_title.headers(columns_width=self.__columns_width, headers_text=self.__headers_text)

        self.canvas = Canvas(self.__frm_main_in, bg=self.__fild_color, highlightthickness=0)
        self.scrollbarX = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas_window.xview, **self.__scroll_button_style)
        self.scrollbarY = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview, **self.__scroll_button_style)
        self.container_in = ctk.CTkFrame(self.canvas, fg_color=self.__fild_color)
        self.__frm_main_in.bind("<Configure>", lambda e: self.canvas_window.configure(scrollregion=self.canvas_window.bbox("all")))
        self.container_in.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window.bind("<Configure>", self.__on_canvas_window_config)
        ####################
        self.canvas_window_id = self.canvas_window.create_window((0, 0), window=self.__frm_main_in, anchor="nw")
        self.canvas.create_window((5, 5), window=self.container_in, anchor="nw")

        self.canvas_window.bind('<Enter>', self.__bind_to_mousewheel)
        self.canvas_window.bind('<Leave>', self.__unbind_from_mousewheel)

        self.canvas.configure(yscrollcommand=self.scrollbarY.set)
        self.canvas_window.configure(xscrollcommand=self.scrollbarX.set)
        ###################
        self.scrollbarX.pack(side="bottom", fill="x")
        self.scrollbarY.pack(side="right", fill="y")
        self.canvas_window.pack(fill=BOTH, expand=True)
        self.__frm_title.pack(fill=X, side=TOP)
        self.canvas.pack(fill=BOTH, expand=True)
        self.__frm_main_out.pack(fill=BOTH, expand=True)
        pass

    def headers(self, columns_width: list[int], headers_text: list[str]):
        self.__frm_title.headers(columns_width, headers_text)
        self.__columns_width = columns_width
        pass

    def heading(self, index: int, text='', command=None, image_on=False):
        self.__frm_title.heading(index, text, command, image_on)
        pass

    def __on_canvas_window_config(self, e):
        self.canvas_window.itemconfig(self.canvas_window_id, height=e.height - 4)
        pass

    def add_data(self, values: list[list[str]]):
        before = dt.now()
        for value in values:
            self.insert(values=value)
        print(dt.now() - before)
        pass

    def __bind_to_mousewheel(self, e):
        if sys.platform == 'win32' or sys.platform == 'darwin':
            self.canvas.bind_all('<MouseWheel>', self.__on_mousewheel)
        elif sys.platform == 'linux' or sys.platform == 'linux2':
            self.canvas.bind_all("<Button-4>", fp(self.__on_mousewheel, scroll=-1))
            self.canvas.bind_all("<Button-5>", fp(self.__on_mousewheel, scroll=1))
        pass

    def __unbind_from_mousewheel(self, e):
        if sys.platform == 'linux' or sys.platform == 'linux2':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")
        pass

    def __on_mousewheel(self, event, scroll=None):
        if self.container_in.winfo_height() > self.canvas.winfo_height():
            if sys.platform == 'linux' or sys.platform == 'linux2':
                self.canvas.yview_scroll(int(scroll), "units")
            else:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        pass

    def selection(self):
        return self.__selection
        pass

    def __get_data_over_item(self, e, data: tuple):
        """Callback function to get values from overed row

        :param data: The data, returned by widget items body
        :return: None
        """
        self.__row_callback_func(e, data)
        pass

    def __get_item_data(self, data):
        if len(self.__selection) > 0:
            self.__selection[3].config_selection(False)
        self.__selection = data
        if len(self.__selection) > 0:
            self.__selection[3].config_selection()
        pass

    def selection_remove(self):
        if len(self.__selection) > 0:
            self.__selection[3].config_selection(False)
        self.__selection = ()
        pass

    def selection_set(self, item: str | int):
        if isinstance(item, int):
            if 0 < item < len(self.__items):
                self.selection_remove()
                for nxt in self.__items:
                    if nxt.iid == f'#{item}':
                        self.__selection = nxt.get_value()
                        self.__selection[3].config_selection()
                        self.see(self.__selection[0])
                        break
        elif isinstance(item, str):
            if item in [nxt.iid for nxt in self.__items]:
                for nxt in self.__items:
                    if nxt.iid == item:
                        self.__selection = nxt.get_value()
                        self.__selection[3].config_selection()
                        self.see(self.__selection[0])
                        break
        pass

    def focus(self, iid: str = '') -> list:
        if not iid:
            return [item.iid for item in self.__items]
        for item in self.__items:
            if iid == item.iid:
                return [item.iid]
        return []
        pass

    def item(self, iid: str = '') -> list:
        if not iid:
            return self.__items
        for item in self.__items:
            if iid == item.iid:
                return [item]
        return []
        pass

    def delete(self, iid: str = '') -> bool:
        nxt_item: ScrolledFrameItem
        if iid:
            for i, nxt_item in enumerate(self.__items):
                if nxt_item.iid == iid:
                    if self.__selection and self.__selection[0] == iid:
                        self.__selection = ()
                    nxt_item.pack_forget()
                    self.__items.pop(i)
                    nxt_item.destroy()
                    return True
        else:
            self.__count = 0
            for nxt_item in self.__items:
                nxt_item.pack_forget()
                nxt_item.destroy()
            # self.container_in.configure(height=self.__frm_main_in.winfo_reqheight(), width=self.__frm_main_in.winfo_reqwidth())
            '''self.container_in.configure(height=self.canvas_window.winfo_height(), width=self.canvas_window.winfo_width())
            self.canvas.configure(height=self.container_in.winfo_reqheight(), width=self.container_in.winfo_reqwidth())
            size = (0, 0, self.winfo_reqheight(), self.winfo_width())
            self.canvas.config(scrollregion=size)'''
            self.see('#0')
            self.canvas_window.xview_moveto(0)
            self.__items = []
            self.__selection = ()
            return True
        return False
        pass

    def count(self) -> int:
        return len(self.__items)
    pass

    def see(self, item: str=None):
        if len(self.__items) == 0:
            return
        move_to = int(item.replace('#', '')) / len(self.__items) if item else 1.0
        if 0 <= move_to <= 1.0:
            self.canvas.yview_moveto(move_to)
        pass

    def get_children(self) -> list:
        return [item.iid for item in self.__items]
        pass

    def right_click_bind(self, event_mod: str, callback: Callable):
        for item in self.__items:
            item.right_click_bind(event_mod, callback)
        pass

    def insert(self, values: list) -> ScrolledFrameItem:
        row_collback = self.__get_data_over_item if self.__row_callback_func else None
        item = ScrolledFrameItem(master=self.container_in, index=self.__count, values=values,
                                 selection_callback=self.__get_item_data,
                                 row_colors=self.__config_row, text_font=self.__text_font,
                                 columns_width=self.__columns_width, row_collback=row_collback,
                                 delete_callback=self.delete)
        self.__items.append(item)
        item.pack(fill=X, expand=True, side=TOP, pady=1)
        self.__count += 1
        return item
        pass

    def stretchedTableConfigure(self, event):
        self.update()
        self.__width = self.canvas.winfo_width()
        self.__height = self.canvas.winfo_height()
        pass

    pass