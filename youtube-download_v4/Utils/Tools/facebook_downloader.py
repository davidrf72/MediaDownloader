import multiprocessing
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from threading import Lock
from tkinter import Tk
from typing import Callable

from customtkinter import CTk

from Utils.Tools.win_message import WinNotifier
from Widgets.scrolled_frame_item2_tk_dinamic import ScrolledFrameItem
from Utils.constants.constants import *
from Utils.Tools.download_process.fb_download_process import FBDownloaderProcess
# https://www.facebook.com/watch?v=1004154427228761


class FaceBookDownloader:
    def __init__(self, parent_window: Tk | CTk, call_back: Callable, progress_handler: ScrolledFrameItem, icon: str):
        self.__in_progress = self.__in_progress
        self.__on_complete = self.__on_complete
        self.__handle_error = self.__handle_error
        self.__icon = icon
        self.__call_back = call_back
        self.__current_downloaded = ''
        self.__parent_window = parent_window
        self.__progress_handler: ScrolledFrameItem = progress_handler
        self.__filename_collector = None
        self.__playlist_index = 0
        self.__playlist_len = 0
        self.__save_location = ''
        self.__url = ''
        self.__task_lock = None
        self.__pipe_sender: Connection = None
        self.__pipe_recv: Connection = None
        self.__download_process = FBDownloaderProcess()
        self.__download_index = ''
        pass

    @property
    def download_index(self):
        return f'{1} from {1}'
        pass

    def start(self, url: str, save_location, logging: bool = True, task_lock: Lock = None):
        self.__task_lock = task_lock
        self.__save_location = save_location
        self.__pipe_sender, self.__pipe_recv = Pipe(duplex=True)
        process = Process(target=self.__download_process.start, args=(url, save_location, self.__pipe_sender), daemon=True)
        process.start()
        while True:
            if self.__pipe_recv.poll():
                res = self.__pipe_recv.recv()
                if res['state'] is None: break
                if res['state'] == 'in_progress':
                    self.__progress(res['progress'], res['button_state'], res['file_count_info'], res['current_downloaded'])
                if res['state'] == 'error':
                    self.__handle_error(res['progress'], res['button_state'], res['file_count_info'], res['current_downloaded'], res['exception'])
                self.__download_index = res['download_index']
            pass
        if logging:
            try:
                if len(res['log_list']) > 0:
                    self.__write_log(res['log_list'])
            except: pass
        self.__on_complete(res['progress'], res['button_state'], res['file_count_info'], res['current_downloaded'])
        pass

    def __progress(self, *args):
        self.__in_progress(*args)
        pass

    def __write_log(self, rows: list):
        with self.__task_lock:
            with open(USER_WORK_FILE_PATH, 'a', encoding='utf-8') as file:
                file.writelines(rows)
            pass
    # -------------------------------------------------------------------------------------------------
    def __in_progress(self, *args):
        progress, state, file_info, current_downloaded = args
        self.__progress_handler.progress = progress
        self.__progress_handler.button_config(state=state)
        self.__progress_handler.file_count_info = file_info
        self.__progress_handler.url = current_downloaded
        self.__parent_window.update_idletasks()
        pass

    def __on_complete(self, *args):
        progress, state, file_info, current_downloaded = args
        self.__progress_handler.file_count_info = file_info
        self.__progress_handler.button_config(state=state)
        if progress > 0:
            notifier = WinNotifier()
            notifier.show(url=current_downloaded, title='Download Complete',
                          message=f'Files was successfully downloaded into {self.__save_location}!',
                          icon_path=self.__icon,
                          duration=5, threaded=True)
        self.__call_back('end')
        pass

    def __handle_error(self, *args):
        progress, state, file_info, current_downloaded, exception_value = args
        self.__progress_handler.file_count_info = file_info
        self.__progress_handler.button_config(state=state)
        self.__progress_handler.exception_value = exception_value
        self.__call_back('error')
        pass
    pass
