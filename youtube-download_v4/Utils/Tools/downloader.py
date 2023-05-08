import multiprocessing
from multiprocessing.connection import Connection
from threading import Lock
from tkinter import Tk
from typing import Callable
from customtkinter import CTk
from Utils.constants.constants import *
from Widgets.scrolled_frame_item2_tk_dinamic import ScrolledFrameItem
from Utils.Tools.win_message import WinNotifier
from multiprocessing import Process, Pipe
from Utils.Tools.download_process.download_process import DownloadProcess

class Downloader:
    def __init__(self, parent_window: Tk | CTk, call_back: Callable, progress_handler: ScrolledFrameItem, icon: str, resolution: str, on_error_tries: int = 5):
        self.__in_progress = self.__in_progress
        self.__on_complete = self.__on_complete
        self.__handle_error = self.__handle_error
        self.__icon = icon
        self.__save_location = ''
        self.__call_back = call_back
        self.__progress_handler: ScrolledFrameItem = progress_handler
        self.__playlist_index = 0
        self.__playlist_len = 0
        self.__resolution = resolution
        self.__current_downloaded = ''
        self.__task_lock = None
        self.__parent_window = parent_window
        self.__pipe_sender: Connection = None
        self.__pipe_recv: Connection = None
        self.__on_error_tries = on_error_tries
        self.__download_process = DownloadProcess(on_error_tries=self.__on_error_tries)
        self.__download_index = ''
        pass

    @property
    def download_index(self):
        return self.__download_index
        pass

    def start(self, url: str, save_location, resolution: str, only_audio: bool = False, logging: bool = True, task_lock: Lock = None):
        self.__task_lock = task_lock
        self.__save_location = save_location
        self.__pipe_sender, self.__pipe_recv = Pipe(duplex=True)
        process = Process(target=self.__download_process.start, args=(url, save_location, resolution, self.__pipe_sender, only_audio), daemon=True)
        process.start()
        res = None
        while True:
            if self.__pipe_recv.poll():
                res = self.__pipe_recv.recv()
                if res['state'] is None: break
                if res['state'] == 'in_progress':
                    self.__in_progress(res['progress'], res['button_state'], res['file_count_info'], res['current_downloaded'])
                if res['state'] == 'end':
                    self.__on_complete(res['progress'], res['button_state'], res['file_count_info'], res['current_downloaded'])
                if res['state'] == 'error':
                    self.__handle_error(res['progress'], res['button_state'], res['file_count_info'],
                                        res['current_downloaded'], res['exception'], res['bad_links'],
                                        res['bad_file_names'])
                    pass
                self.__download_index = res['download_index']
            pass
        try:
            if len(res['log_list']) > 0:
                if logging:
                    self.__write_log(res['log_list'])
        except:
            pass
        self.__call_back('end')
        pass

    def __write_log(self, rows: list):
        with self.__task_lock:
            with open(USER_WORK_FILE_PATH, 'a', encoding='utf-8') as file:
                file.writelines(rows)
                pass
        pass
    #-------------------------------------------------------------------------------------------------

    def __in_progress(self, *args):
        progress, state, file_info, current_downloaded = args
        self.__progress_handler.progress = progress
        self.__progress_handler.button_config(state=state)
        self.__progress_handler.file_count_info =file_info
        self.__progress_handler.url = current_downloaded
        self.__parent_window.update_idletasks()
        pass

    def __on_complete(self, *args):
        progress, state, file_info, current_downloaded = args
        self.__progress_handler.progress = progress
        self.__progress_handler.file_count_info = file_info
        self.__progress_handler.button_config(state=state)
        notifier = WinNotifier()
        notifier.show(url=current_downloaded, title='Download Complete',
                             message=f'Files was successfully downloaded into {self.__save_location}!',
                             icon_path=self.__icon,
                             duration=5, threaded=True)
        pass

    def __handle_error(self, *args):
        progress, state, file_info, current_downloaded, exception_value, bad_links, bad_file_names = args
        self.__progress_handler.file_count_info = file_info
        self.__progress_handler.button_config(state=state)
        self.__progress_handler.exception_value = (exception_value, bad_links, bad_file_names)
        self.__call_back('error')
        pass

    pass