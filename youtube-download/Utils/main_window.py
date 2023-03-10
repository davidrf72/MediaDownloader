import pathlib
import tkinter
import customtkinter as ctk
from tkinter.constants import *
from tkinter import ttk, filedialog, messagebox, Menu
from PIL import Image
from threading import Thread

class MainWindow(ctk.CTk):
    def __init__(self, backend, **kw):
        super(MainWindow, self).__init__(**kw)
        self.geometry('500x640+800+200')
        self.title('Youtube media downloader')
        self.__cur_path = pathlib.Path(__file__).parent.parent
        self.iconbitmap(self.__cur_path.joinpath('social_youtube_2756.ico'))
        self.run_backend = backend
        self.__logo_image = None
        self.__title_image = None
        self.__saved_file = ''
        self.__popup = None
        self.__popup_widget = None
        self.overrideredirect(True)
        self.__build_window()
        self.mainloop()
        pass

    def __build_window(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelframe.Label', background='blue', font=('Times', 14, 'italic'), foreground='lightgreen')
        style.configure('TLabelframe', background='blue', foreground='red')

        self.frm_title = ctk.CTkFrame(self, fg_color='darkblue', corner_radius=60, height=40)
        self.frm_title.pack(fill=X, padx=2, pady=2)
        self.frm_title.bind("<B1-Motion>", self.__move_window)
        self.frm_title.bind("<Button-1>", self.__save_last_xy)
        self.frm_title.bind("<Map>", self.__normal_size_window)
        self.frm_title.bind("<Enter>", self.__header_cursor_active)
        self.frm_title.bind("<Leave>", self.__header_cursor_deactive)

        self.frm_main = ctk.CTkFrame(self, fg_color='blue', corner_radius=60)
        self.frm_main.pack(fill=BOTH, expand=True, padx=2, pady=2)

        self.frm_label = ttk.LabelFrame(self.frm_main, labelanchor=N, relief='groove')
        self.frm_label.place(x=30, y=10, width=440, height=560)
        font = ctk.CTkFont(family='Times', size=24, weight='bold')
        lbl_to_frame = ctk.CTkLabel(self.frm_main, fg_color='darkblue', bg_color='blue', text_color='red', text='Get video from youtube')
        lbl_to_frame.configure(corner_radius=30, font=font, height=50)
        lbl_to_frame.place(x=100, y=10, relwidth=0.6)
        #-------------------------------self.frm_title------------------------------
        self.__title_image = ctk.CTkImage(Image.open(self.__cur_path.joinpath('social_youtube_2756.ico')), size=(32, 32))
        self.lbl_title_icon = ctk.CTkLabel(self.frm_title, fg_color='darkblue', height=32, width=32, image=self.__title_image)
        self.lbl_title_icon.configure(text='')
        self.lbl_title_icon.place(y=5, x=10)

        font = ctk.CTkFont(family='Times', size=16, weight='bold')
        self.lbl_title = ctk.CTkLabel(self.frm_title, fg_color='darkblue', height=32)
        self.lbl_title.configure(text='Youtube media downloader', text_color='white', font=font)
        self.lbl_title.place(y=5, x=55)

        font = ctk.CTkFont(family='Times', size=12, weight='bold')
        self.btn_close_window = ctk.CTkButton(self.frm_title, text='❌', fg_color="#3B8ED0")
        self.btn_close_window.configure(cursor='hand2', font=font, command=self.on_closing)
        self.btn_close_window.configure(hover_color='red', width=30, height=30)
        self.btn_close_window.place(y=5, x=460)
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
        self.txt_to_link.place(relwidth=1)

        self.frm_file = ttk.LabelFrame(self.frm_label, labelanchor=NW, border=0, text='Save to...')
        self.frm_file.place(relx=0.05, rely=0.45, relwidth=0.9, relheight=0.12)
        font = ctk.CTkFont(family='Times', size=12, weight='bold')
        self.txt_to_file = ctk.CTkEntry(self.frm_file, text_color='red', placeholder_text=r'File_Name.mp4', placeholder_text_color='silver')
        self.txt_to_file.configure(corner_radius=30, font=font, height=40)
        self.txt_to_file.bind("<Button-3>", self.__menu_popup)
        self.txt_to_file.place(relwidth=0.7)
        font = ctk.CTkFont(family='Times', size=14, weight='bold')
        self.btn_file = ctk.CTkButton(self.frm_file, text='Save in', text_color='black', hover_color='red')
        self.btn_file.configure(corner_radius=30, font=font, height=40, command=self.__save_to)
        self.btn_file.place(relx=0.72, relwidth=0.28)

        font = ctk.CTkFont(family='Times', size=24, weight='bold')
        self.btn_download = ctk.CTkButton(self.frm_label, text_color='black', text='Download', hover_color='red')
        self.btn_download.configure(corner_radius=30, font=font, width=200, height=60, command=self.__download)
        self.btn_download.place(x=100, rely=0.65)

        font = ctk.CTkFont(family='Times', size=20, weight='bold')
        self.frm_state = ttk.LabelFrame(self.frm_label, labelanchor=NW, border=1, text='State...')
        self.frm_state.place(relx=0.05, rely=0.78, relwidth=0.9, relheight=0.2)
        self.lbl_state = ctk.CTkLabel(self.frm_state, text_color='red', fg_color='blue', text='🎵🎵🎵🎵')
        self.lbl_state.configure(corner_radius=30, font=font, height=60)
        self.lbl_state.place(relx=0.05, rely=0.06, relwidth=0.9)
        self.prg_state = ctk.CTkProgressBar(self.frm_state, progress_color='red')
        self.prg_state.set(0)
        #self.prg_state.place(relx=0.05, rely=0.83, relwidth=0.9)
        #----------------------------self.__popup---------------------------------------------
        menu_style = {'tearoff': 0, 'activebackground': 'red', 'activeforeground': 'blue', 'font': ('Times', 14, 'bold'), 'foreground': 'lightgreen', 'bg': 'blue'}
        state = 'normal'
        self.__popup = Menu(self, menu_style)
        self.__popup.add_command(label='Paste', state=state, command=self.__paste_link)
        self.__popup.add_separator()
        self.__popup.add_command(label='Clear', state=state, command=lambda: self.__popup_widget.delete(0, END))
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

    def set_backend(self, backend):
        self.run_backend = backend
        pass

    def __save_to(self):
        file_types = [('MP4', '*.mp4'), ('All Files', '*.*')]
        file_path = filedialog.asksaveasfilename(initialdir=self.__cur_path, filetypes=file_types, title='Save to...')
        if file_path:
            file_path = file_path if file_path.lower().endswith('.mp4') else f'{file_path}.mp4'
            self.txt_to_file.delete(0, END)
            self.txt_to_file.insert(0, file_path)
        pass

    def __download(self):
        if not self.txt_to_link.get() or not self.txt_to_file.get():
            messagebox.showerror(title='An error', message='Please enter URL and destination path', parent=self)
            return
        if not self.txt_to_link.get().lower().startswith(r'https://www.youtube.com/'):
            messagebox.showerror(title='An error', message='Not valid link', parent=self)
            return
        else:
            tmp_file = '/'.join(self.txt_to_file.get().replace('\\', '/').split('/')[:-1])
            if not pathlib.Path(tmp_file).exists():
                messagebox.showerror(title='An error', message='Path does not exists', parent=self)
                return
            self.__config_on_start('start')
            path = pathlib.Path(self.txt_to_file.get()) if self.txt_to_file.get().lower().endswith('.mp4') else pathlib.Path(f'{self.txt_to_file.get()}.mp4')
            Thread(target=self.run_backend, args=(self.txt_to_link.get(), path, self.__in_progress, self.__on_complete, self.__handle_error)).start()
            #self.run_backend(self.txt_to_link.get(), path, self.__in_progress, self.__on_complete, self.__handle_error)
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
                self.txt_to_file.delete(0, END)
                self.btn_download.configure(state='normal')
                pass
            case 'error':
                self.prg_state.set(0)
                self.prg_state.place_forget()
                self.btn_download.configure(state='normal')
                pass
            case _:
                raise ValueError('Unknown state in "__config_on_start"')
                pass
        pass

    def __in_progress(self, *args):
        progress = float(1) - float(args[-1] / args[0].filesize)
        self.prg_state.set(progress)
        self.lbl_state.configure(text="Download In Progress...")
        self.update_idletasks()
        pass

    def __on_complete(self, *args):
        self.lbl_state.configure(text="Download Complete")
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

    def on_closing(self):
        self.destroy()
        pass

    pass

