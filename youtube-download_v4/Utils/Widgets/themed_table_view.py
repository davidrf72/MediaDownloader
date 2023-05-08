import sys
from tkinter import *
from tkinter import ttk
from typing import Literal, Any
import customtkinter as ctk
from PIL import Image, ImageTk
from Utils.constants.constants import *


class TableView(ctk.CTkFrame):
    def __init__(self, master: Tk | Frame | LabelFrame, headers: list, values: list, columns_width: list[int],
                 records_per_page: int = 10, pagination=True, search_enabled=True, sort_keys: list=None, selectmode=BROWSE, **kw):
        """Construct a TableView widget with the parent MASTER.
Valid resource names: background, bd, bg, borderwidth, class, colormap, container,
cursor, height, highlightbackground, highlightcolor, highlightthickness, relief,
takefocus, visual, width.

        :param master: Parent widget
        :param headers: List of headers - list[str]
        :param values: Values list - list[list[str]]
        :param columns_width: List of columns width - list[int]
        :param records_per_page: Number of records per page
        :param pagination: True to make page view, False to view all data
        :param search_enabled: True to view search bar
        :param selectmode: Selection method to treeview widget
        :param kw: TableView frame styling options

        **kw
             width: int = 200,
             height: int = 200,
             corner_radius: int | str | None = None,
             border_width: int | str | None = None,
             bg_color: str | tuple[str, str] = "transparent",
             fg_color: str | tuple[str, str] | None = None,
             border_color: str | tuple[str, str] | None = None,
             background_corner_colors: tuple[str | tuple[str, str]] | None = None,
             overwrite_preferred_drawing_method: str | None = None,
             **kwargs: Any
        """
        super(TableView, self).__init__(master=master, **kw)
        self.__mouse_wheel_id = ''
        self.__mouse_wheel_linux_4_id = ''
        self.__mouse_wheel_linux_5_id = ''
        self.__header_select_image = ImageTk.PhotoImage(Image.open(RESOURCES_32_PATH.joinpath('select_ok_accept_32.png')))
        self.__init_variables(headers, values, columns_width, records_per_page, pagination, search_enabled, sort_keys, selectmode)
        self.__build_frame()
        self.__start_table()
        pass

    def __validate_params(self, headers: list, values: list, columns_width: list[int], records_per_page: int, sort_keys: list = None) -> bool:
        if records_per_page <= 0:
            return False
        for nxt in columns_width:
            if not isinstance(nxt, int):
                return False
        if not isinstance(headers, list) or not isinstance(values, list):
            return False
        for nxt in values:
            if not isinstance(nxt, list):
                return False
        if len(headers) == 0:
            return False
        if len(values) > 0 and len(values[0]) != len(headers):
            return False
        if sort_keys is not None:
            if len(sort_keys) != len(headers):
                return False
            pass
        return True
        pass

    def clear(self):
        self.repopulate(headers=self.__header, values=[], columns_width=self.__column_width,
                        records_per_page=self.__records_per_page, pagination=self.__pagination,
                        search_enabled=self.__search_enabled, selectmode=self.__selectmode)
        self.lbl_opt_page_count.configure(text=f'{0}')
        pass

    def repopulate(self, headers: list, values: list, columns_width: list[int],
                 records_per_page: int = 10, pagination=True, search_enabled=True, sort_keys: list=None, selectmode=BROWSE):
        self.__init_variables(headers, values, columns_width, records_per_page, pagination, search_enabled, sort_keys, selectmode)
        self.__tree_treeview.configure(selectmode=selectmode)
        self.__reorg_widgets()
        self.__start_table()
        pass

    def __reorg_widgets(self):
        btn_style_ctk = {'fg_color': 'skyblue', 'font': ('Times', 18), 'corner_radius': 30, 'width': 60,
                         'height': 50, 'text_color': 'black', 'hover_color': 'red'}
        self.__tree_treeview.delete(*self.__tree_treeview.get_children())
        self.__tree_treeview.config(columns=self.__header)
        for i, nxt in enumerate(self.__header, start=1):
            self.__tree_treeview.heading(column=f'#{i}', text=nxt, command=lambda index=i: self.__sort(index - 1))
            self.__tree_treeview.column(column=nxt, width=self.__column_width[i - 1], stretch=False)
        self.cmb_search.configure(values=self.__header)
        self.cmb_search.set(self.__header[0])
        if self.__pagination or not self.__search_enabled:
            self.frm_controls.pack(fill=X)
        else:
            self.frm_controls.pack_forget()
        if self.__pagination:
            self.frm_opt.pack(fill=BOTH, expand=True, side=BOTTOM)
        if not self.__search_enabled:
            self.sep_2 = ttk.Separator(self.frm_opt, orient=VERTICAL)
            self.sep_2.grid(row=0, column=9, sticky='ns', padx=(10, 10))
            self.btn_enable_search = ctk.CTkButton(self.frm_opt, text='Search ⬇', **btn_style_ctk, command=self.__enable_search)
            self.btn_enable_search.grid(row=0, column=10, sticky='nwes')
        else:
            self.sep_2.grid_forget()
            self.btn_enable_search.grid_forget()
        pass

    def __init_variables(self, headers: list, values: list, columns_width: list[int],
                 records_per_page: int = 10, pagination=True, search_enabled=True, sort_keys: list = None, selectmode=BROWSE):
        if len(headers) != len(columns_width):
            raise ValueError('Headers list is not same length such columns width list')
        if not self.__validate_params(headers, values, columns_width, records_per_page, sort_keys):
            raise ValueError('One of arguments invalid')
        self.__values = values
        self.__header = headers
        self.__selection_direction = []
        self.__sort_keys = []
        for _ in self.__header:
            self.__selection_direction.append(False)
        self.__sort_keys = sort_keys
        self.__column_width = columns_width
        self.__records_per_page = records_per_page
        self.__page_num = 0
        self.__paginated_value = []
        self.__current_page = 0
        self.__current_search_records = []
        self.__search_enabled = not search_enabled
        self.__in_search = False
        self.__pagination = pagination
        self.__selectmode = selectmode
        self.__button_1_pressed = None
        pass

    def __start_table(self):
        if self.__pagination:
            self.__tree_pagination()
        else:
            self.__build_tree()
            pass
        self.__enable_search()
        pass

    '''
    [('Combobox.downarrow', {'side': 'left', 'sticky': 'ns'}), ('Combobox.field', {'sticky': 'nswe', 'children': [('Combobox.padding', {'sticky': 'nswe', 'children': [('Combobox.textarea', {'sticky': 'nswe'})]})]})]

    '''

    def __build_frame(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TSeparator', background='black')
        self.style.configure('Treeview', rowheight=35, font=('Times', 14))
        self.style.configure('Treeview.Heading', font=('Times', 18, 'bold'), background='skyblue', relief='sunken')
        self.style.map('Treeview.Heading', background=[('active', 'red')], relief=[('active', 'raized')])
        self.style.configure("Treeview.Heading", font=('Times', 18, 'bold'))

        self.style.map('TCombobox', background=[('active', 'red'), ('!disabled', 'blue')],
                       fieldbackground=[("!disabled", "silver")],
                       foreground=[("focus", "black"), ("!disabled", "blue")])
        self.style.layout('TCombobox', layoutspec=[
            ('Combobox.downarrow', {'side': 'right', 'sticky': 'ns'}),
            ('Combobox.field', {'sticky': 'nswe', 'children':
                [('Combobox.padding',
                  {'sticky': 'nswe', 'children':
                      [('Combobox.textarea', {'sticky': 'nswe'})
                       ]})
                ]})
            ])
        self.option_add('*TCombobox*Listbox.font', ('Times', 16, 'italic'))
        self.option_add('*TCombobox*Listbox.foreground', 'black')
        self.option_add('*TCombobox*Listbox.background', 'OliveDrab1')
        self.option_add('*TCombobox*Listbox*selectBackground', 'OliveDrab2')
        self.option_add('*TCombobox*Listbox*selectForeground', 'blue')

        self.style.configure('table.TLabelframe.Label', background='silver', font=('Times', 14, 'italic'), foreground='lightgreen')
        self.style.configure('table.TLabelframe', background='silver', foreground='black')

        self.frm_main = ctk.CTkFrame(self, fg_color='skyblue')
        self.frm_main.pack(fill=BOTH, expand=True)

        self.frm_treeview = ctk.CTkFrame(self.frm_main)
        self.frm_treeview.pack(fill=BOTH, expand=True)
        self.frm_controls = ctk.CTkFrame(self.frm_main)
        if self.__pagination or not self.__search_enabled:
            self.frm_controls.pack(fill=X)
        # ----------------------------------self.frm_treeview-----------------------------------------
        self.scr_tree_x = Scrollbar(self.frm_treeview, orient=HORIZONTAL)
        self.scr_tree_y = Scrollbar(self.frm_treeview, orient=VERTICAL)
        self.__tree_treeview = ttk.Treeview(self.frm_treeview, selectmode=self.__selectmode, yscrollcommand=self.scr_tree_y.set,
                                            xscrollcommand=self.scr_tree_x.set)
        self.__tree_treeview.config(show='headings')
        if sys.platform == 'win32' or sys.platform == 'darwin':
            self.__mouse_wheel_id = self.__tree_treeview.bind('<MouseWheel>', self.__mouse_wheel)
        elif sys.platform == 'linux' or sys.platform == 'linux2':
            self.__mouse_wheel_linux_4_id = self.__tree_treeview.bind('<Button-4>', self.__mouse_wheel)
            self.__mouse_wheel_linux_5_id = self.__tree_treeview.bind('<Button-5>', self.__mouse_wheel)
        self.scr_tree_x.configure(command=self.__tree_treeview.xview)
        self.scr_tree_y.configure(command=self.__tree_treeview.yview)
        self.scr_tree_x.pack(fill=X, side=BOTTOM)
        self.scr_tree_y.pack(fill=Y, side=RIGHT)
        self.__tree_treeview.pack(fill=BOTH, expand=True, side=LEFT)
        self.__tree_treeview.config(columns=self.__header)
        for i, nxt in enumerate(self.__header, start=1):
            self.__tree_treeview.heading(column=f'#{i}', text=nxt, command=lambda index=i: self.__sort(index-1))
            self.__tree_treeview.column(column=nxt, width=self.__column_width[i - 1], stretch=False)
        # ----------------------------------self.frm_controls-----------------------------------------
        btn_style_ctk = {'fg_color': 'skyblue', 'font': ('Times', 18), 'corner_radius': 30, 'width': 60,
                         'height': 50, 'text_color': 'black', 'hover_color': 'red'}
        self.frm_search = ttk.LabelFrame(self.frm_controls, style='table.TLabelframe')
        lbl_search = ctk.CTkLabel(self.frm_search, text='Search', font=('Times', 20, 'italic'), fg_color='silver', bg_color='silver', corner_radius=30)
        self.frm_search.configure(labelwidget=lbl_search, labelanchor=NW)
        self.frm_search.pack(fill=X, side=TOP)
        self.txt_search = ctk.CTkEntry(self.frm_search, font=('Times', 20), width=200, height=40, fg_color='silver', bg_color='silver')
        self.txt_search.bind('<Return>', self.__search)
        self.txt_search.bind('<Escape>', self.__stop_search)
        self.txt_search.pack(side=LEFT, pady=5, padx=(5, 5))
        self.cmb_search = ttk.Combobox(self.frm_search, font=('Times', 20), values=self.__header, width=15)
        self.cmb_search.set(self.__header[1])
        self.cmb_search.pack(side=LEFT, padx=(5, 10))
        img = ctk.CTkImage(dark_image=Image.open(RESOURCES_32_PATH.joinpath('xmag_search_find_export_locate_32.png')), size=(32, 32))
        self.btn_search = ctk.CTkButton(self.frm_search, text='', image=img, command=lambda: self.__search(None), **btn_style_ctk, bg_color='silver')
        self.btn_search.image = img
        self.btn_search.pack(side=LEFT, padx=(0, 10))
        self.lbl_search_pages = ctk.CTkLabel(self.frm_search, text='', font=('Times', 20), height=50, width=80, fg_color='skyblue', bg_color='silver', corner_radius=30)
        self.lbl_search_pages.pack(side=LEFT)
        self.btn_search_stop = ctk.CTkButton(self.frm_search, text='❌', command=lambda e: self.__stop_search(None), **btn_style_ctk)
        self.btn_search_stop.configure(font=('Times', 14, 'bold'), state='disabled', text_color_disabled='orange', text_color='red', bg_color='silver')
        self.btn_search_stop.pack(side=LEFT, padx=(10, 0))

        self.frm_opt = ctk.CTkFrame(self.frm_controls, corner_radius=0)
        self.frm_opt.pack(fill=BOTH, expand=True, side=BOTTOM)
        lbl_opt_page = ctk.CTkLabel(self.frm_opt, text='Page', font=('Times', 20), width=80, fg_color='skyblue', corner_radius=30)
        lbl_opt_page.grid(row=0, column=0, sticky='nwes')

        def page_num_validate(next_char):
            if next_char.isdigit(): return True
            return False
            pass
        self.txt_opt_page_cur = ctk.CTkEntry(self.frm_opt, font=('Times', 20), width=80, fg_color='skyblue', corner_radius=20)
        reg = self.register(func=page_num_validate)
        self.txt_opt_page_cur.configure(validate='key', validatecommand=(reg, '%S'))
        self.txt_opt_page_cur.configure(justify='center')
        self.txt_opt_page_cur.insert(END, f'{self.__current_page + 1}')
        self.txt_opt_page_cur.grid(row=0, column=1, sticky='nwes')
        self.txt_opt_page_cur.bind('<Return>', lambda e: self.move_to_page(int(self.txt_opt_page_cur.get()) if self.txt_opt_page_cur.get() else self.__current_page+1))

        lbl_opt_page_of = ctk.CTkLabel(self.frm_opt, text='of', font=('Times', 20), width=60, fg_color='skyblue', corner_radius=30)
        lbl_opt_page_of.grid(row=0, column=2, sticky='nwes')
        self.lbl_opt_page_count = ctk.CTkLabel(self.frm_opt, text=f'{self.__page_num}', font=('Times', 20), width=80, fg_color='skyblue', corner_radius=20)
        self.lbl_opt_page_count.grid(row=0, column=3, sticky='nwes')
        sep_1 = ttk.Separator(self.frm_opt, orient=VERTICAL)
        sep_1.grid(row=0, column=4, sticky='ns', padx=(10, 10))
        self.btn_first = ctk.CTkButton(self.frm_opt, text='⏮', **btn_style_ctk, command=self.__set_first)
        self.btn_first.grid(row=0, column=5, sticky='nwes')
        self.btn_prev = ctk.CTkButton(self.frm_opt, text='◀', **btn_style_ctk, command=self.__set_prev)
        self.btn_prev.grid(row=0, column=6, sticky='nwes', padx=(0, 5))
        self.btn_next = ctk.CTkButton(self.frm_opt, text='▶', **btn_style_ctk, command=self.__set_next)
        self.btn_next.grid(row=0, column=7, sticky='nwes')
        self.btn_last = ctk.CTkButton(self.frm_opt, text='⏭', **btn_style_ctk, command=self.__set_last)
        self.btn_last.grid(row=0, column=8, sticky='nwes')
        self.sep_2 = ttk.Separator(self.frm_opt, orient=VERTICAL)
        self.btn_enable_search = ctk.CTkButton(self.frm_opt, text='Search ⬇', **btn_style_ctk, command=self.__enable_search)
        if not self.__search_enabled:
            self.sep_2.grid(row=0, column=9, sticky='ns', padx=(10, 10))
            self.btn_enable_search.grid(row=0, column=10, sticky='nwes')
        pass

    @property
    def values_count(self):
        return len(self.__values)
        pass

    @property
    def current_page_items(self):
        if self.__pagination:
            return self.__paginated_value[self.__current_page]
        return self.__values

    @property
    def values(self):
        return self.__values
        pass

    def __sort(self, index: int):
        if not self.__sort_keys:
            return
        if self.__sort_keys[index]:
            if not self.__in_search:
                for i in range(1, len(self.__header)+1):
                    self.__tree_treeview.heading(column=f'#{i}', image='')
                self.__tree_treeview.heading(column=f'#{index + 1}', image=self.__header_select_image)
                self.__values = sorted(self.__values, key=lambda x: self.__sort_keys[index](index, x), reverse=self.__selection_direction[index])
                self.__selection_direction[index] = not self.__selection_direction[index]
                self.__tree_pagination(self.__current_page)
            pass
        pass

    def __init_treeview(self, page: int = -1):
        self.__tree_treeview.delete(*self.__tree_treeview.get_children())
        self.lbl_search_pages.configure(text='')
        self.txt_search.delete(0, END)
        #page = page if page + 1 <= self.__page_num else page - 1
        if len(self.__values) == 0:
            tmp_val = []
        else:
            tmp_val = self.__values if page == -1 else self.__paginated_value[page]
        for i, nxt in enumerate(tmp_val):
            self.__tree_treeview.insert(parent='', index=END, iid=f'#{i}', values=nxt)
        pass

    def __tree_pagination(self, start_page=-1):
        if len(self.__values) == 0:
            self.__init_treeview()
            self.txt_opt_page_cur.delete(0, END)
            self.txt_opt_page_cur.insert(END, f'{self.__current_page}')
            return
        self.__page_num = len(self.__values) // self.__records_per_page
        if len(self.__values) / self.__records_per_page != len(self.__values) // self.__records_per_page:
            self.__page_num += 1
        self.lbl_opt_page_count.configure(text=f'{self.__page_num}')
        self.__paginated_value = []
        for i in range(self.__page_num):
            tmp_list = self.__values[i * self.__records_per_page:i * self.__records_per_page + self.__records_per_page]
            self.__paginated_value.append(tmp_list)
        self.__current_page = self.__current_page if start_page == -1 else start_page
        self.__current_page = self.__current_page if self.__current_page + 1 <= self.__page_num else self.__current_page - 1
        self.txt_opt_page_cur.delete(0, END)
        self.txt_opt_page_cur.insert(END, f'{self.__current_page + 1}')
        self.__init_treeview(self.__current_page)
        pass

    def __mouse_wheel_bind(self):
        if self.__pagination and not self.__in_search:
            if sys.platform == 'win32' or sys.platform == 'darwin':
                self.__tree_treeview.unbind('<MouseWheel>', self.__mouse_wheel_id)
            elif sys.platform == 'linux' or sys.platform == 'linux2':
                self.__tree_treeview.unbind('<Button-4>', self.__mouse_wheel_linux_4_id)
                self.__tree_treeview.unbind('<Button-5>', self.__mouse_wheel_linux_5_id)
        else:
            if sys.platform == 'win32' or sys.platform == 'darwin':
                self.__mouse_wheel_id = self.__tree_treeview.bind('<MouseWheel>', self.__mouse_wheel)
            elif sys.platform == 'linux' or sys.platform == 'linux2':
                self.__mouse_wheel_linux_4_id = self.frm_search.bind('<Button-4>', self.__mouse_wheel)
                self.__mouse_wheel_linux_5_id = self.frm_search.bind('<Button-5>', self.__mouse_wheel)
        pass

    def __search(self, e):
        self.__mouse_wheel_bind()
        self.__in_search = True
        self.btn_search_stop.configure(state='normal')
        self.frm_opt.pack_forget()
        self.__current_search_records = []
        row_index = self.__header.index(self.cmb_search.get())
        tmp_values = [(nxt_row, i) for i, nxt_row in enumerate(self.__values) if nxt_row[row_index].lower().count(self.txt_search.get().lower())]
        self.__tree_treeview.delete(*self.__tree_treeview.get_children())
        self.lbl_search_pages.configure(text=f'{len(tmp_values)}')
        for i, nxt in enumerate(tmp_values):
            self.__current_search_records.append(nxt[1])
            self.__tree_treeview.insert(parent='', index=END, iid=f'#{i}', values=nxt[0])
        pass

    def __stop_search(self, e):
        if self.__in_search:
            self.__mouse_wheel_bind()
            self.__in_search = False
            self.btn_search_stop.configure(state='disabled')
            if self.__pagination:
                self.frm_opt.pack(fill=BOTH, expand=True, side=BOTTOM)
                self.__tree_pagination(self.__current_page)
                self.__set_current_page(self.__current_page + 1)
            else:
                self.__init_treeview()
        pass

    def __build_tree(self):
        self.__init_treeview()
        self.frm_opt.pack_forget()
        pass

    def __enable_search(self):
        if self.__search_enabled:
            self.frm_search.pack_forget()
            #if not self.__search_enabled:
            self.btn_enable_search.configure(text='Search ⬆')
            self.__search_enabled = False
        else:
            self.frm_search.pack(fill=X, side=TOP)
            if not self.__search_enabled:
                self.btn_enable_search.configure(text='Search ⬇')
            self.__search_enabled = True
        pass

    def set_records_per_page(self, records_per_page: int):
        if records_per_page > 0:
            self.__records_per_page = records_per_page
            self.__current_page = 0
            self.__tree_pagination()
        pass

    def move_to_page(self, page_num: int):
        if 0 < page_num <= self.__page_num:
            if self.__current_page + 1 == page_num:
                self.__set_current_page(page_num)
                return
            self.__init_treeview(page_num - 1)
            self.__current_page = page_num - 1
            self.__set_current_page(page_num)
        elif self.__page_num == 0:
            self.txt_opt_page_cur.delete(0, END)
            self.txt_opt_page_cur.insert(0, '0')
            pass
        else:
            self.move_to_page(self.__current_page + 1)
        pass

    def __mouse_wheel(self, e):
        if e.delta == 120:
            self.__set_next()
        elif e.delta == -120:
            self.__set_prev()
        pass

    def __set_first(self):
        self.__init_treeview(0)
        self.__current_page = 0
        self.__set_current_page(self.__current_page + 1)
        pass

    def __set_last(self):
        self.__init_treeview(self.__page_num - 1)
        self.__current_page = self.__page_num - 1
        self.__set_current_page(self.__current_page + 1)
        pass

    def __set_prev(self):
        if self.__current_page > 0:
            self.__current_page -= 1
            self.__set_current_page(self.__current_page + 1)
            self.__init_treeview(self.__current_page)
        pass

    def __set_next(self):
        if self.__current_page < self.__page_num - 1:
            self.__current_page += 1
            self.__set_current_page(self.__current_page + 1)
            self.__init_treeview(self.__current_page)
        pass

    def __set_current_page(self, page_num: int):
        page_num = page_num if len(self.__values) > 0 else 0
        self.txt_opt_page_cur.delete(0, END)
        self.txt_opt_page_cur.insert(END, f'{page_num}')
        pass

    def bind_tree(self, event_ident: str, call_back_func):
        self.__tree_treeview.bind(event_ident, lambda e: call_back_func({'x': e.x, 'y': e.y, 'x_root': e.x_root, 'y_root': e.y_root, 'state': e.state}))
        pass

    def selection(self) -> tuple[str, ...]:
        return self.__tree_treeview.selection()
        pass

    def item(self, item: str, option=None, **kw):
        '''if option is None:
            self.__tree_treeview.item(item, **kw)
            return None'''
        return self.__tree_treeview.item(item, option=option, **kw)

    def focus(self, item: None = ...):
        if item is None:
            return self.__tree_treeview.focus()
        self.__tree_treeview.focus(item=item)
        return None

    def get_children(self, item: str | None = None) -> tuple[str, ...]:
        return self.__tree_treeview.get_children(item=item)

    def identify_column(self, x: int) -> str:
        return self.__tree_treeview.identify_column(x=x)
        pass

    def identify_region(self, x: int, y: int) -> Literal["heading", "separator", "tree", "cell", "nothing"]:
        return self.__tree_treeview.identify_region(x, y)
        pass

    def identify_row(self, y: int) -> str:
        return self.__tree_treeview.identify_row(y)
        pass

    def identify_element(self, x: int, y: int) -> str:
        return self.__tree_treeview.identify_element(x, y)
        pass

    def identify(self, component, x: int, y: int) -> str:
        return self.__tree_treeview.identify(component, x, y)
        pass

    def heading(self, column: int):
        return self.__tree_treeview.heading(column=column)
        pass

    def selection_set(self, items: str | list[str] | tuple[str, ...]):
        self.__tree_treeview.selection_set(items)
        pass

    def selection_add(self, items: str | list[str] | tuple[str, ...]):
        self.__tree_treeview.selection_add(items)
        pass

    def selection_remove(self, items: str | list[str] | tuple[str, ...]):
        self.__tree_treeview.selection_remove(items)
        pass

    def selection_clear(self, **kw: Any):
        self.__tree_treeview.selection_clear(**kw)
        pass

    def delete(self) -> None:
        selected_indexes = []
        if self.__in_search:
            for nxt_item in self.__tree_treeview.selection():
                index = int(nxt_item.replace('#', ''))
                self.__tree_treeview.delete(nxt_item)
                selected_indexes.insert(0, self.__current_search_records[index])
            for nxt in selected_indexes:
                self.__values.pop(nxt)
            return
        if self.__pagination:
            for nxt_item in self.__tree_treeview.selection():
                avg_index = 0
                index = int(nxt_item.replace('#', ''))
                for i in range(self.__current_page):
                    avg_index += self.__records_per_page
                index += avg_index
                selected_indexes.insert(0, index)
            for nxt in selected_indexes:
                self.__values.pop(nxt)
            self.__tree_pagination(self.__current_page)
        else:
            for nxt_item in self.__tree_treeview.selection():
                selected_indexes.insert(0, int(nxt_item.replace('#', '')))
            for nxt in selected_indexes:
                self.__values.pop(nxt)
            self.__init_treeview()
        pass

    def insert(self, values: list | tuple[Any, ...] = ...) -> str:
        """Creates a new item

        :param values:
        :param iid:
        :return: Return the item identifier of the newly created item.
        """
        if self.__in_search:
            self.__stop_search()
        if not isinstance(values, list) or len(values) != len(self.__header):
            raise ValueError('Not valid argument')
        self.__values.append(values)
        if self.__pagination:
            self.__tree_pagination()
            self.__set_last()
        else:
            self.__init_treeview()
            self.__tree_treeview.see(self.__tree_treeview.get_children()[-1])
        return self.__tree_treeview.get_children()[-1]
        pass

    #-------------------------events-------------------------------------------------------------------
    """
    region              meaning
    heading             heading area.
    separator           Space between two columns headings.
    tree                The tree area.
    cell                A data cell.
    """

    def bind_button_1_pressed(self, func_name):
        self.__button_1_pressed = func_name
        pass

    def __btn_released_1(self, e):
        if self.__tree_treeview.identify_region(e.x, e.y) == 'tree' or self.__tree_treeview.identify_region(e.x, e.y) == 'cell':
            if self.__button_1_pressed:
                self.__button_1_pressed(e.x, e.y)
        pass

    pass
