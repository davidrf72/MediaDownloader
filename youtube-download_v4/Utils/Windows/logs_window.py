import datetime
import webbrowser
from tkinter import *
import customtkinter as ctk
from Utils.Widgets.themed_table_view import TableView
from Utils.constants.constants import *


class LogsWindow(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk | Tk = None, **kwargs):
        super(LogsWindow, self).__init__(master, **kwargs)
        self.__master = master
        self.__title = 'Download history'
        self.title(self.__title)
        self.bad_symbol = ['#', '.', ':', '/']
        self.sort_keys = None
        #self.iconbitmap(bitmap=str(RESOURCES_32_PATH.joinpath('activities-history-log_32.ico')))
        self.wm_protocol('WM_DELETE_WINDOW', lambda: self.__on_child_close(None))
        self.__master.wm_attributes("-disabled", True)
        self.__master.wm_attributes("-alpha", 0.5)
        self.transient(self.__master)
        self.resizable(False, False)
        self.bind_all('<BackSpace>', self.__on_child_close)
        self.__load_data()
        self.__build_window()
        pass

    def __load_data(self):
        string_key = lambda i, x: x[i]
        def date_key(index: int, data_list: list[str]):
            datetime_list = data_list[index].split(' ')
            date_list = datetime_list[0].split('/')
            time_list = datetime_list[1].split(':')
            return datetime.datetime(year=int(date_list[2]), month=int(date_list[0]), day=int(date_list[1]), hour=int(time_list[0]), minute=int(time_list[1]))
            pass

        self.sort_keys = [string_key, string_key, string_key, string_key, date_key]
        with open(USER_WORK_FILE_PATH, mode='r', encoding='utf-8') as fl:
            self.header = fl.readline().strip().split(',')
            self.data_list = [line.strip().split(',') for line in fl.readlines()]
            self.columns_width = [400, 300, 300, 150, 200]
        pass

    def __build_window(self):
        self.frm_main = ctk.CTkFrame(self)
        self.frm_main.pack(fill=BOTH, expand=True)

        self.frm_tree = ctk.CTkFrame(self.frm_main)
        self.frm_tree.pack(fill=BOTH, expand=True, side=LEFT)

        self.frm_controls = ctk.CTkFrame(self.frm_main)
        self.frm_controls.pack(fill=Y, side=RIGHT)

        #-----------------------------------------self.frm_tree----------------------------------------------------
        self.trv_logs = TableView(self.frm_tree, headers=self.header,
                             values=self.data_list, columns_width=self.columns_width, records_per_page=10,
                             pagination=True, search_enabled=True, sort_keys=self.sort_keys)
        self.trv_logs.pack(fill=BOTH, expand=True)
        self.trv_logs.bind_tree('<Double-1>', self.__double_click)
        self.trv_logs.bind_tree('<Motion>', self.__tree_mouse_move)
        self.trv_logs.bind_tree('<Leave>', self.__tree_mouse_leave)
        # -----------------------------------------self.frm_controls-----------------------------------------------
        self.btn_remove = ctk.CTkButton(self.frm_controls, text='Remove', **BUTTON_STYLE, command=self.__remove_item)
        self.btn_remove.grid(column=0, row=0, padx=10, pady=5, sticky='we')
        self.btn_clear = ctk.CTkButton(self.frm_controls, text='Clear all', **BUTTON_STYLE, command=self.__remove_all)
        self.btn_clear.grid(column=0, row=1, padx=10, pady=5, sticky='we')
        self.btn_open_file = ctk.CTkButton(self.frm_controls, text='Open file', **BUTTON_STYLE, command=lambda: self.__open_item(0))
        self.btn_open_file.grid(column=0, row=2, padx=10, pady=5, sticky='we')
        self.btn_open_path = ctk.CTkButton(self.frm_controls, text='Open location', **BUTTON_STYLE, command=lambda: self.__open_item(1))
        self.btn_open_path.grid(column=0, row=3, padx=10, pady=5, sticky='we')
        self.btn_open_url = ctk.CTkButton(self.frm_controls, text='Open link', **BUTTON_STYLE, command=lambda: self.__open_item(2))
        self.btn_open_url.grid(column=0, row=4, padx=10, pady=5, sticky='we')
        self.btn_save = ctk.CTkButton(self.frm_controls, text='Save and exit', **BUTTON_STYLE, command=self.__save)
        self.btn_save.grid(column=0, row=5, padx=10, pady=5, sticky='we')
        self.btn_cancel = ctk.CTkButton(self.frm_controls, text='Cancel', **BUTTON_STYLE, command=lambda: self.__on_child_close(None))
        self.btn_cancel.grid(column=0, row=6, padx=10, pady=5, sticky='we')

        self.lbl_info = ctk.CTkLabel(self.frm_controls, text='',  height=100, font=('Times', 20, 'bold'))
        self.lbl_info.configure(fg_color='blue', text_color='lightgreen', corner_radius=30)
        self.lbl_info.grid(column=0, row=7, padx=10, pady=5, sticky='nsew')
        self.__set_info()
        pass

    def __on_child_close(self, e):
        self.destroy()
        self.__master.wm_attributes("-disabled", False)
        self.__master.wm_attributes("-alpha", 1)
        self.__master.child_window = None
        self.__master.lift()
        pass

    def __set_info(self):
        records = self.trv_logs.values_count
        self.lbl_info.configure(text=f'Records: {records}')
        pass

    def __tree_mouse_move(self, e):
        row_iid = self.trv_logs.identify_row(e['y'])
        if row_iid:
            row_val = self.trv_logs.item(row_iid)['values']
            i_path = f'{row_val[1]}/{row_val[0]}'
            if os.path.exists(i_path):
                self.title(f'{self.__title} -- {i_path}')
            else:
                self.title(f'{self.__title} -- File: "{row_val[0]}" not exists')
        else:
            self.title('Download history')
        pass

    def __tree_mouse_leave(self, e):
        self.title('Download history')
        pass

    def __double_click(self, e):
        if self.trv_logs.identify_region(e['x'], e['y']) == 'cell':
            column_index = int(self.trv_logs.identify_column(e['x']).replace('#', '')) - 1
            row_iid = self.trv_logs.identify_row(e['y'])
            row_val = self.trv_logs.item(row_iid)['values']
            item = row_val[column_index]
            match column_index:
                case 0:
                    if row_val[3] != 'None':
                        ext = item[-4:]
                        name = item[:-4]
                        for nxt in self.bad_symbol:
                            name = name.replace(nxt, '')
                        item = name + ext

                    i_path = f'{row_val[1]}/{item}'
                    if os.path.exists(i_path):
                        os.startfile(i_path)
                case 1:
                    if os.path.exists(item):
                        os.startfile(item)
                    pass
                case 2:
                    webbrowser.open(item, new=2)
                    pass
        pass

    def __save(self):
        with open(USER_WORK_FILE_PATH, mode='w', encoding='utf-8') as fl:
            fl.write(','.join(self.header) + '\n')
            for nxt in self.trv_logs.values:
                fl.write(','.join(nxt) + '\n')
                pass
        self.__on_child_close(None)
        pass

    def __remove_item(self):
        if self.trv_logs.selection():
            self.trv_logs.delete()
            self.__set_info()
        pass

    def __remove_all(self):
        if self.trv_logs.get_children():
            '''self.trv_logs.repopulate(headers=self.header, values=[], columns_width=self.columns_width,
                                     records_per_page=10, pagination=True, search_enabled=True)'''
            self.trv_logs.clear()
            self.__set_info()
        pass

    def __open_item(self, index: int):
        if self.trv_logs.selection():
            value = self.trv_logs.item(self.trv_logs.selection()[0])['values']
            row_value = value[index]
            match index:
                case 0:
                    ext = row_value[-4:]
                    name = row_value[:-4]
                    for nxt in self.bad_symbol:
                        name = name.replace(nxt, '')
                    row_value = name + ext
                    i_path = f'{value[1]}/{row_value}'
                    if os.path.exists(i_path):
                        os.startfile(i_path)
                case 1:
                    if os.path.exists(row_value):
                        os.startfile(row_value)
                    pass
                case 2:
                    webbrowser.open(row_value, new=2)
                    pass
            pass
        pass
    pass
