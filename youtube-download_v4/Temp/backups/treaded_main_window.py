import sys
import threading
import tkinter
import webbrowser
from time import sleep

import customtkinter as ctk
from tkinter.constants import *
from tkinter import ttk, filedialog, messagebox, Menu
from PIL import Image
from threading import Thread
from Utils.Tools.win_message import WinNotifier
from Utils.Tools.downloader import Downloader
from Utils.constants.constants import *
from Utils.Tools.conf import Settings
from Utils.Windows.logs_window import LogsWindow
from Utils.Tools.facebook_downloader import FaceBookDownloader
from Widgets.scrolled_frame_widget import ScrolledFrame
from datetime import datetime as dt

if getattr(sys, 'frozen', False):
    import pyi_splash
    pass

class MainWindow(ctk.CTk):
    def __init__(self, **kw):
        super(MainWindow, self).__init__(**kw)
        self.geometry('500x640+700+200')
        self.title('Youtube media downloader')
        self.__cur_path = CURRENT_PATH
        self.iconbitmap(self.__cur_path.joinpath('social_youtube_2756.ico'))
        self.wm_protocol('WM_DELETE_WINDOW', lambda: self.on_closing(None))
        self.child_window = None
        self.__logo_image = None
        self.__title_image = None
        self.__saved_file = ''
        self.__popup = None
        self.__popup_widget = None
        self.__saved_file_path = ''
        self.__only_audio_var = ctk.StringVar(value='Video and audio')
        self.__settings_default = {'resolution': 'Highest resolution', 'Save_path': f'{USER_DATA}', 'only_audio': f'{self.__only_audio_var.get()}', 'logging': True}
        self.__settings = {}
        self.__cur_resolution = 'Highest resolution'
        self.__cur_save_path = ''
        self.__cur_only_audio = ''
        self.__do_log_var = ctk.BooleanVar(value=True)
        self.__do_log_var.trace('w', self.__trace_do_log_var)
        self.__cur_logging = True
        self.__size_flag = False
        self.overrideredirect(True)
        self.__build_window()
        self.__load_settings()
        #self.__add_data()
        self.downloader = Downloader(self.__in_progress, self.__on_complete, self.__handle_error, self.__cur_resolution)
        self.fb_downloader = FaceBookDownloader(self.__in_fb_progress, self.__on_complete, self.__handle_error)
        if getattr(sys, 'frozen', False):
            pyi_splash.close()
        self.mainloop()
        pass

    def __load_settings(self):
        settings = Settings('Settings.json', self.__settings_default)
        self.__settings = settings.read_config()
        save_path = self.__settings['Save_path'] if pathlib.Path(self.__settings['Save_path']).exists() else str(USER_DATA)
        if not pathlib.Path(self.__settings['Save_path']).exists():
            self.__settings['Save_path'] = str(USER_DATA)
            settings.write_config(self.__settings)
            pass
        self.cmb_resolution.set(self.__settings['resolution'])
        self.txt_start_folder.delete(0, END)
        self.txt_start_folder.insert(0, save_path)
        self.txt_to_file.insert(0, save_path)
        self.__cur_resolution = self.__settings['resolution']
        self.__cur_save_path = save_path
        self.__cur_only_audio = self.__settings['only_audio']
        self.__only_audio_var.set(value=self.__cur_only_audio)
        self.__do_log_var.set(value=self.__settings['logging'])
        self.__cur_logging = self.__do_log_var.get()
        pass

    def __change_size(self):
        if not self.__size_flag:
            self.geometry(f'1300x640+{self.winfo_rootx()}+{self.winfo_rooty()}')
            self.btn_title_settings_icon.place(y=5, x=1210)
            self.btn_close_window.place(y=5, x=1250)
            self.frm_main.place(relx=0, y=40, relwidth=0.39)
            self.frm_progress.place(relx=0.4, y=40, relwidth=0.6)
            self.frm_tree_progress.place(relx=0, y=0, relwidth=1, relheight=1)
            self.tree_progress.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
            self.__size_flag = True
            self.__add_data()
            threading.Thread(target=self.set_progress, daemon=True).start()
        else:
            self.geometry(f'500x640+{self.winfo_rootx()}+{self.winfo_rooty()}')
            self.btn_title_settings_icon.place(y=5, x=410)
            self.btn_close_window.place(y=5, x=450)
            self.frm_main.place(relx=0, y=40, relwidth=1)
            self.tree_progress.place_forget()
            self.frm_tree_progress.place_forget()
            self.frm_progress.place_forget()
            self.__size_flag = False
        pass

    def set_progress(self):
        for i in range(1, 11):
            self.cur_item.progress = i / 10
            sleep(1)
        self.cur_item.file_count_info = 'Download completed'
        self.cur_item.button_config(state='normal')
        pass

    def __add_data(self):
        values = ['https://www.youtube.com/watch?v=bPm_QLt_ogk', f'{(0 + 1) / 100}', f'File Nº: {1} from: {1}', '']
        self.cur_item = self.tree_progress.insert(values=values)
        self.cur_item.button_config(state='disabled')
        pass

    '''def __add_data(self):
        before = dt.now()
        for i in range(100):
            values = ['https://www.youtube.com/watch?v=bPm_QLt_ogk', f'{(i + 1) / 100}', f'File Nº: {1} from: {i + 1}', '']  # (1, i + 1)]
            self.cur_item = self.tree_progress.insert(values=values)
        print(dt.now() - before)
        pass'''

    def __build_window(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelframe.Label', background='blue', font=('Times', 14, 'italic'), foreground='lightgreen')
        style.configure('TLabelframe', background='blue', foreground='red')

        self.frm_title = ctk.CTkFrame(self, fg_color='darkblue', corner_radius=60, height=600)
        #self.frm_title.pack(fill=X, side=TOP, padx=2, pady=2)
        self.frm_title.place(relx=0, y=0, relwidth=1)
        self.frm_title.bind("<B1-Motion>", self.__move_window)
        self.frm_title.bind("<Button-1>", self.__save_last_xy)
        self.frm_title.bind("<Map>", self.__normal_size_window)
        self.frm_title.bind("<Enter>", self.__header_cursor_active)
        self.frm_title.bind("<Leave>", self.__header_cursor_deactive)

        self.frm_progress = ctk.CTkFrame(self, fg_color='darkblue', corner_radius=60, height=600)

        self.frm_tree_progress = ctk.CTkFrame(self.frm_progress, fg_color='blue', corner_radius=60, height=600)
        self.tree_progress = ScrolledFrame(master=self.frm_tree_progress, headers_text=['Source url', 'Progress', 'File count', 'Buttons'],
                                           scroll_button_colors=('blue', 'darkblue', 'red'),
                                           header_colors=('darkblue', 'blue', 'red', 'lightgreen', 'blue'),
                                           row_colors=('white', 'grey', 'blue', 'blue'), field_color='blue',
                                           header_font=('Times', 30, 'bold'), text_font=('Ariel', 12), height=400)

        self.frm_main = ctk.CTkFrame(self, fg_color='blue', corner_radius=60, height=600)
        self.frm_main.place(relx=0, y=50, relwidth=1)

        self.frm_label = ttk.LabelFrame(self.frm_main, labelanchor=N, relief='groove')
        self.frm_label.place(x=30, y=10, width=440, height=560)
        font = ctk.CTkFont(family='Times', size=24, weight='bold')
        lbl_to_frame = ctk.CTkLabel(self.frm_main, fg_color='darkblue', bg_color='blue', text_color='red', text='Get video from youtube')
        lbl_to_frame.configure(corner_radius=30, font=font, height=50)
        lbl_to_frame.place(x=100, y=10, relwidth=0.6)

        self.frm_main.update()
        self.frm_menu = ctk.CTkFrame(self.frm_main, fg_color='blue', corner_radius=20, width=300, height=self.frm_main.winfo_height())
        self.frm_menu.configure(border_width=4, border_color='black')

        self.frm_menu_about = ctk.CTkFrame(self.frm_main, fg_color='blue', corner_radius=20, width=300, height=self.frm_main.winfo_height())
        self.frm_menu_about.configure(border_width=4, border_color='black')
        #-------------------------------self.frm_menu_about-------------------------
        frm_about_opt = ttk.LabelFrame(self.frm_menu_about, labelanchor=N, border=1, text='', padding=10)
        frm_about_opt.place(relx=0.03, rely=0.02, relwidth=0.93, relheight=0.95)
        lbl_resolution_opt = ctk.CTkLabel(self.frm_menu_about, fg_color='darkblue', bg_color='blue', text_color='red', text='About')
        lbl_resolution_opt.configure(corner_radius=30, font=font, height=40)
        lbl_resolution_opt.place(x=25, y=18, relwidth=0.8)

        font = ctk.CTkFont(family='Times', size=18, weight='bold')
        frm_about_info = ttk.LabelFrame(frm_about_opt, labelanchor=NW, border=1, text='Application info', padding=10)
        frm_about_info.place(relx=0.01, y=25, relwidth=0.98, relheight=0.85)

        txt_style = {'fg_color': 'blue', 'font': font, 'height': 40, 'corner_radius': 15, 'border_width': 0, 'text_color': 'lightgreen', 'state': 'readonly'}
        txt_about_app_name = ctk.CTkEntry(frm_about_info)
        txt_about_app_name.insert(0, 'Media downloader')
        txt_about_app_name.configure(**txt_style)
        txt_about_app_name.place(relx=0.01, rely=0, relwidth=0.98)

        txt_about_app_ver = ctk.CTkEntry(frm_about_info)
        txt_about_app_ver.insert(0, 'ver: 2.1.5')
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
        self.btn_menu_ok = ctk.CTkButton(frm_menu_about_buttons, text='O.K.', command=lambda: self.__open_menu_about(None), **BUTTON_STYLE)
        self.btn_menu_ok.pack()
        #-------------------------------self.frm_menu-------------------------------
        frm_resolution_opt = ttk.LabelFrame(self.frm_menu, labelanchor=N, border=1, text='', padding=10)
        frm_resolution_opt.place(relx=0.03, rely=0.02, relwidth=0.93, relheight=0.95)
        lbl_resolution_opt = ctk.CTkLabel(self.frm_menu, fg_color='darkblue', bg_color='blue', text_color='red', text='Settings')
        lbl_resolution_opt.configure(corner_radius=30, font=font, height=40)
        lbl_resolution_opt.place(x=25, y=18, relwidth=0.8)

        frm_resolution = ttk.LabelFrame(frm_resolution_opt, labelanchor=NW, border=1, text='Source resolution', padding=10)
        frm_resolution.place(relx=0.01, rely=0.04, relwidth=0.98, relheight=0.15)
        res_list = ['Highest resolution', 'Lowest resolution']
        for nxt in RESOLUTIONS.keys():
            res_list.append(nxt)
        self.cmb_resolution = ctk.CTkComboBox(frm_resolution, values=res_list, **COMBO_STYLE)
        self.cmb_resolution.set(res_list[0])
        self.cmb_resolution.pack(fill=BOTH)

        font = ctk.CTkFont(family='Times', size=12, weight='bold')
        frm_start_folder = ttk.LabelFrame(frm_resolution_opt, labelanchor=NW, border=1, text='Save folder', padding=10)
        frm_start_folder.place(relx=0.01, rely=0.21, relwidth=0.98, relheight=0.3)
        self.txt_start_folder = ctk.CTkEntry(frm_start_folder, corner_radius=30, text_color='black', placeholder_text='Dir name')
        self.txt_start_folder.configure(corner_radius=30, font=font, height=40)
        self.txt_start_folder.bind("<Button-3>", self.__menu_popup)
        self.txt_start_folder.place(relx=0, rely=0.05, relwidth=1)
        self.txt_start_folder.insert(0, CURRENT_PATH)
        self.btn_start_folder = ctk.CTkButton(frm_start_folder, text='📂...', command=self.__save_settings, **BUTTON_STYLE)
        self.btn_start_folder.configure(text_color='lightgreen')
        self.btn_start_folder.place(relx=0.5, rely=0.52)

        only_audio = ['Video and audio', 'Audio only']
        frm_menu_only_audio = ttk.LabelFrame(frm_resolution_opt, labelanchor=NW, border=1, text='Audio only', padding=10)
        frm_menu_only_audio.place(relx=0.01, rely=0.53, relwidth=0.98, relheight=0.15)
        self.chk_only_audio = ctk.CTkComboBox(frm_menu_only_audio, **COMBO_STYLE, values=only_audio, variable=self.__only_audio_var)
        self.chk_only_audio.pack(fill=BOTH)

        frm_menu_do_log = ttk.LabelFrame(frm_resolution_opt, labelanchor=NW, border=1, text='Logging', padding=10)
        frm_menu_do_log.place(relx=0.01, rely=0.7, relwidth=0.98, relheight=0.15)
        self.chk_do_log = ctk.CTkSwitch(frm_menu_do_log, onvalue=True, offvalue=False, variable=self.__do_log_var, font=('Times', 18, 'bold'), text='Save log', text_color='black')
        self.chk_do_log.configure(button_color='darkblue', button_hover_color='red', progress_color='green')
        self.chk_do_log.pack(side=LEFT)
        self.btn__do_log = ctk.CTkButton(frm_menu_do_log, text='Logs', **BUTTON_STYLE, command=self.__view_logs)
        self.btn__do_log.configure(width=80)
        self.btn__do_log.pack(side=RIGHT)

        frm_menu_buttons = ctk.CTkFrame(frm_resolution_opt, fg_color='blue')
        frm_menu_buttons.place(relx=0.02, rely=0.92)
        self.btn_menu_ok = ctk.CTkButton(frm_menu_buttons, text='O.K.', command=lambda: self.__open_menu(None, True), **BUTTON_STYLE)
        self.btn_menu_ok.grid(row=0, column=0, padx=(0, 5))
        self.btn_menu_cancel = ctk.CTkButton(frm_menu_buttons, text='Cancel', command=lambda: self.__open_menu(None), **BUTTON_STYLE)
        self.btn_menu_cancel.grid(row=0, column=1)
        #-------------------------------self.frm_title------------------------------
        self.__title_image = ctk.CTkImage(Image.open(self.__cur_path.joinpath('social_youtube_2756.ico')), size=(32, 32))
        self.lbl_title_icon = ctk.CTkLabel(self.frm_title, fg_color='darkblue', height=32, width=32, image=self.__title_image)
        self.lbl_title_icon.bind('<ButtonRelease-1>', self.__open_menu_about)
        self.lbl_title_icon.bind('<ButtonRelease-3>', self.__open_menu_about)
        self.lbl_title_icon.configure(text='', cursor='hand2')
        self.lbl_title_icon.place(y=5, x=10)

        font = ctk.CTkFont(family='Times', size=16, weight='bold')
        self.lbl_title = ctk.CTkLabel(self.frm_title, fg_color='darkblue', height=32)
        self.lbl_title.configure(text='Youtube media downloader', text_color='white', font=font)
        self.lbl_title.place(y=5, x=50)

        font = ctk.CTkFont(family='Times', size=14, weight='bold')
        self.btn_title_settings_icon = ctk.CTkButton(self.frm_title, text='⚙', text_color='black', font=font)
        self.btn_title_settings_icon.bind('<ButtonRelease-1>', self.__open_menu)
        self.btn_title_settings_icon.bind('<ButtonRelease-3>', self.__open_menu)
        self.btn_title_settings_icon.configure(cursor='hand2',hover_color='red', width=30, height=30, fg_color='#3B8ED0')
        self.btn_title_settings_icon.place(y=5, x=410)

        self.btn_close_window = ctk.CTkButton(self.frm_title, text='❌', fg_color="#3B8ED0")
        self.btn_close_window.configure(cursor='hand2', font=font, command=lambda: self.on_closing(None))
        self.btn_close_window.configure(hover_color='red', width=30, height=30)
        self.btn_close_window.place(y=5, x=450)
        #-------------------------------self.frm_label-------------------------------
        self.__logo_image = Image.open(self.__cur_path.joinpath('YouTube-Logo.png'))
        self.__logo_image = ctk.CTkImage(self.__logo_image, size=(300, 200))

        self.lbl_logo = ctk.CTkLabel(self.frm_label, text='', height=200, fg_color='silver')
        self.lbl_logo.configure(corner_radius=30, image=self.__logo_image, fg_color='blue')
        self.lbl_logo.place(relx=0.01, rely=0.04, relwidth=0.98, relheight=0.25)

        self.frm_link = ttk.LabelFrame(self.frm_label, labelanchor=NW, border=0, text='Source link')
        self.frm_link.place(relx=0.05, rely=0.3, relwidth=0.9, relheight=0.12)
        font = ctk.CTkFont(family='Times', size=12, weight='bold')
        self.txt_to_link = ctk.CTkEntry(self.frm_link, text_color='red', placeholder_text=r'https://www.youtube.com/...', placeholder_text_color='silver')
        self.txt_to_link.configure(corner_radius=30, font=font, height=40)
        self.txt_to_link.bind("<Button-3>", self.__menu_popup)
        self.txt_to_link.bind('<Return>', self.__download)
        self.txt_to_link.place(relwidth=1)

        self.frm_file = ttk.LabelFrame(self.frm_label, labelanchor=NW, border=0, text='Save to...')
        self.frm_file.place(relx=0.05, rely=0.45, relwidth=0.9, relheight=0.12)
        font = ctk.CTkFont(family='Times', size=12, weight='bold')
        self.txt_to_file = ctk.CTkEntry(self.frm_file, text_color='red', placeholder_text='Dir name', placeholder_text_color='silver')
        self.txt_to_file.configure(corner_radius=30, font=font, height=40)
        self.txt_to_file.bind("<Button-3>", self.__menu_popup)
        self.txt_to_file.bind("<Return>", self.__save_to)
        self.txt_to_file.place(relwidth=0.7)
        font = ctk.CTkFont(family='Times', size=14, weight='bold')
        self.btn_file = ctk.CTkButton(self.frm_file, text='Save in', text_color='black', hover_color='red')
        self.btn_file.configure(corner_radius=30, font=font, height=40, command=lambda: self.__save_to(None))
        self.btn_file.place(relx=0.72, relwidth=0.28)

        font = ctk.CTkFont(family='Times', size=24, weight='bold')
        self.btn_download = ctk.CTkButton(self.frm_label, text_color='black', text='Download', hover_color='red')
        self.btn_download.configure(corner_radius=30, font=font, width=200, height=60, command=self.__change_size) #, command=lambda: self.__download(None))
        self.btn_download.place(x=100, rely=0.65)

        font = ctk.CTkFont(family='Times', size=20, weight='bold')
        self.frm_state = ttk.LabelFrame(self.frm_label, labelanchor=NW, border=1, text='State...')
        self.frm_state.place(relx=0.05, rely=0.78, relwidth=0.9, relheight=0.2)
        self.lbl_state = ctk.CTkLabel(self.frm_state, text_color='red', fg_color='blue', text='🎵🎵🎵🎵')
        self.lbl_state.configure(corner_radius=30, font=font, height=60)
        self.lbl_state.place(relx=0.05, rely=0.11, relwidth=0.9)
        self.prg_state = ctk.CTkProgressBar(self.frm_state, progress_color='red')
        self.prg_state.set(0)
        #----------------------------self.__popup---------------------------------------------
        menu_style = {'tearoff': 0, 'activebackground': 'red', 'activeforeground': 'blue', 'font': ('Times', 14, 'bold'), 'foreground': 'lightgreen', 'bg': 'blue'}
        state = 'normal'
        self.__popup = Menu(self, menu_style)
        self.__popup.add_command(label='Paste', state=state, command=self.__paste_link)
        self.__popup.add_separator()
        self.__popup.add_command(label='Clear', state=state, command=lambda: self.__popup_widget.delete(0, END))
        pass

    def __view_logs(self):
        if not self.child_window:
            self.child_window = LogsWindow(self)
        self.__open_menu(None)
        pass

    def __open_menu_about(self, e):
        if self.frm_menu_about.place_info():
            self.frm_menu_about.place_forget()
        else:
            if self.frm_menu.place_info():
                self.__open_menu(e=None)
            self.frm_menu_about.place(x=0, y=0)
        pass

    def __open_menu(self, e, if_save=False):
        if self.frm_menu.place_info():
            self.frm_menu.place_forget()
            if if_save:
                settings = Settings('Settings.json', self.__settings_default)
                self.__cur_resolution = self.cmb_resolution.get()
                self.txt_to_file.delete(0, END)
                self.txt_to_file.insert(0, self.txt_start_folder.get())
                self.__cur_save_path = self.txt_start_folder.get()
                self.__cur_only_audio = self.__only_audio_var.get()
                self.__cur_logging = self.__do_log_var.get()
                settings.write_config({'resolution': self.__cur_resolution, 'Save_path': self.__cur_save_path, 'only_audio': self.__cur_only_audio, 'logging': self.__cur_logging})
            else:
                self.cmb_resolution.set(self.__cur_resolution)
                self.txt_start_folder.delete(0, END)
                self.txt_start_folder.insert(0, self.__cur_save_path)
                self.__only_audio_var.set(value=self.__cur_only_audio)
                self.__do_log_var.set(value=self.__cur_logging)
        else:
            if self.frm_menu_about.place_info():
                self.__open_menu_about(None)
            self.frm_menu.place(x=0, y=0)
        pass

    def __save_settings(self):
        dir_name = filedialog.askdirectory(initialdir=USER_DATA, title='Save to...', parent=self)
        if dir_name:
            self.txt_start_folder.delete(0, END)
            self.txt_start_folder.insert(0, dir_name)
        pass

    def __close_menu(self, e):
        if self.frm_menu.place_info():
            if e.widget.master is not self.lbl_title_icon:
                self.frm_menu.place_forget()
        pass

    def __trace_do_log_var(self, *args):
        color = 'black' if self.__do_log_var.get() else '#7F8487'
        for nxt in self.chk_do_log.winfo_children():
            if type(nxt) is tkinter.Label:
                nxt.configure(fg=color)
        pass

    def __menu_popup(self, event):
        """Showing of popup menu and saving of current treeview y coordinates
__paste_link
        :param event: Event object
        :return: None
        """
        event.widget.focus_set()
        self.__popup_widget = event.widget
        try:
            state = 'normal' if self.clipboard_get() else 'disabled'
        except tkinter.TclError:
            state = 'disabled'
        self.__popup.entryconfig('Paste', state=state)
        state = 'normal' if self.__popup_widget.get() else 'disabled'
        self.__popup.entryconfig('Clear', state=state)
        try:
            self.__popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.__popup.grab_release()
        pass

    def __paste_link(self):
        self.__popup_widget.delete(0, END)
        self.__popup_widget.insert(END, self.clipboard_get())
        pass

    def __save_to(self, e):
        initdir = USER_DATA if not pathlib.Path(self.txt_to_file.get()).exists() else pathlib.Path(self.txt_to_file.get())
        dir_name = filedialog.askdirectory(initialdir=initdir, title='Save to...', parent=self)
        if dir_name:
            self.txt_to_file.delete(0, END)
            self.txt_to_file.insert(0, dir_name)
        pass

    def __download(self, e):
        if not self.txt_to_link.get() or not self.txt_to_file.get():
            messagebox.showerror(title='An error', message='Please enter URL and destination path', parent=self)
            return
        if not self.txt_to_link.get().lower().startswith(r'https://www.youtube.com/') and\
                not self.txt_to_link.get().lower().startswith(r'https://www.facebook.com/') and\
                not self.txt_to_link.get().lower().startswith(r'https://fb.watch/'):
            messagebox.showerror(title='An error', message='Not valid link', parent=self)
            return
        else:
            if not pathlib.Path(self.txt_to_file.get()).exists():
                messagebox.showerror(title='An error', message='Path does not exists', parent=self)
                return
            self.__config_on_start('start')
            self.__saved_file_path = self.txt_to_file.get()
            if self.txt_to_link.get().lower().startswith(r'https://www.facebook.com/') or self.txt_to_link.get().lower().startswith(r'https://fb.watch/'):
                Thread(target=self.fb_downloader.start, args=(self.txt_to_link.get(), self.__saved_file_path, self.__cur_logging), daemon=True).start()
            else:
                audio_only = True if self.__only_audio_var.get() == 'Audio only' else False
                Thread(target=self.downloader.start, args=(self.txt_to_link.get(), self.__saved_file_path, self.__cur_resolution, audio_only, self.__cur_logging), daemon=True).start()
        pass

    def __config_on_start(self, state: str):
        match state:
            case 'start':
                self.lbl_state.configure(text="Download In Progress")
                self.prg_state.place(relx=0.05, rely=0.83, relwidth=0.9)
                self.btn_download.configure(state='disabled')
                pass
            case 'end':
                self.prg_state.set(0)
                self.prg_state.place_forget()
                self.btn_download.configure(state='normal')
                self.lbl_title.configure(text='Youtube media downloader')
                pass
            case 'error':
                self.prg_state.set(0)
                self.prg_state.place_forget()
                self.btn_download.configure(state='normal')
                self.lbl_title.configure(text='Youtube media downloader')
                pass
            case _:
                raise ValueError('Unknown state in "__config_on_start"')
                pass
        pass

    def __in_progress(self, *args):
        progress = float(1) - float(args[-1] / args[0].filesize)
        self.prg_state.set(progress)
        self.lbl_state.configure(text="Download In Progress...")
        self.lbl_title.configure(text=f'Youtube media downloader: file Nº - {self.downloader.download_index}')
        self.update_idletasks()
        pass

    def __in_fb_progress(self, *args):
        progress = float(1) - float((args[0]['total_bytes']-args[0]['downloaded_bytes']) / args[0]['total_bytes'])
        self.prg_state.set(progress)
        self.lbl_state.configure(text="Download In Progress...")
        self.lbl_title.configure(text=f'Youtube media downloader: file Nº - {self.fb_downloader.download_index}')
        self.update_idletasks()
        pass

    def __on_complete(self, *args):
        self.lbl_state.configure(text="Download Complete")
        notifier = WinNotifier()
        notifier.show(url=self.txt_to_file.get(), title='Download Complete',
                             message=f'Files was successfully downloaded into {self.__saved_file_path}!',
                             icon_path=self.__cur_path.joinpath('social_youtube_2756.ico'),
                             duration=5, threaded=True)
        self.__config_on_start('end')
        pass

    def __handle_error(self, *args):
        self.lbl_state.configure(text="Something went wrong, try again")
        self.__config_on_start('error')
        pass

    #---------------------------------------------------------------------------------------------
    def __move_window(self, e):
        x, y = e.x - self.last_click_x + self.winfo_x(), e.y - self.last_click_y + self.winfo_y()
        self.geometry(f"+{x}+{y}")
        pass

    def __save_last_xy(self, e):
        self.last_click_x = e.x
        self.last_click_y = e.y
        pass

    def __header_cursor_active(self, e):
        self.frm_title.configure(cursor="fleur")
        pass

    def __header_cursor_deactive(self, e):
        self.frm_title.configure(cursor="arrow")
        pass

    def header_button_collor_active(self, e):
        e.widget["fg_color"] = "red"
        pass

    def header_button_collor_deactive(self, e):
        e.widget["fg_color"] = "#3B8ED0"
        pass

    def __minimaise_window(self):
        self.overrideredirect(False)
        self.iconify()
        pass

    def __normal_size_window(self, e):
        self.deiconify()
        self.overrideredirect(True)
        pass

    def on_closing(self, e):
        self.destroy()
        pass

    pass

