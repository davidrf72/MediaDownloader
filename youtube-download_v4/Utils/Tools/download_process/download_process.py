import datetime
from typing import Callable

from pytube import YouTube, request, Playlist
from Utils.constants.constants import *
from multiprocessing.connection import Connection

request.default_range_size = 500000


class DownloadProcess:
    def __init__(self, on_error_tries: int = 5):
        self.__url = ''
        self.__save_location = ''
        self.__resolution = ''
        self.__only_audio = False
        self.__playlist_index = 0
        self.__playlist_len = 0
        self.__conn_sender = None
        self.__playlist_index = 0
        self.__playlist_len = 0
        self.__errors_list = []
        self.__error_reload = ''
        self.__on_error_tries = on_error_tries
        self.__error_download_attempts = int(on_error_tries / 2) if on_error_tries >= 4 else 2
        self.__current_attempt = 0
        pass

    @property
    def error_download_attempts(self):
        return self.__error_download_attempts
        pass

    @error_download_attempts.setter
    def error_download_attempts(self, val: int):
        self.__error_download_attempts = val if isinstance(val, int) and val >= 0 else 2
        pass

    @property
    def download_index(self) -> str:
        return f'{self.__playlist_len - self.__playlist_index} from {self.__playlist_len}{self.__error_reload}'
        pass

    @staticmethod
    def clear_filename(file_name: str, file_ext: str = '') -> str:
        bad_symbols = r',!()[]{}@#$%^&*.?<>=+|\\/-~`:;"\''
        ext = file_name[-4:] if not file_ext else f'.{file_ext}'
        name = file_name[:-4] if not file_ext else file_name
        tmp_name = ''.join([sym for sym in name if sym not in bad_symbols])
        return f'{tmp_name}{ext}'
        pass

    def __get_video(self, url, save_location, file_suffix: str, only_audio: bool = False, on_error_tries: int = 0) -> str:
        try:
            download = YouTube(url, on_progress_callback=self.__in_progress,
                               on_complete_callback=self.__on_complete_inner)
            if only_audio:
                stream = download.streams.filter(only_audio=True).first()
            else:
                stream = download.streams.filter(progressive=True).get_highest_resolution()
            filename = self.clear_filename(download.title, file_suffix)
            row = ','.join([filename, save_location, url, str(only_audio),
                            datetime.datetime.now().strftime('%m/%d/%Y %H:%M')]) + '\n'
            stream.download(filename=filename, output_path=save_location)
            # print(f'on_error_tries: {on_error_tries} -- {filename}')
            return row
        except Exception as e:
            self.__error = True
            # print(f'error: {e}')
            if on_error_tries == 0:
                self.__errors_list.append((e, url))
                return ''
            else:
                return self.__get_video(url, save_location, file_suffix, only_audio, on_error_tries-1)

    def __get_video_iitag(self, url, save_location, file_suffix: str, only_audio: bool = False, on_error_tries: int = 0) -> str:
        try:
            download = YouTube(url, on_progress_callback=self.__in_progress,
                               on_complete_callback=self.__on_complete_inner) #, use_oauth=True, allow_oauth_cache=True)
            if only_audio:
                stream = download.streams.filter(only_audio=True).first()
            else:
                stream = download.streams.get_by_itag(RESOLUTIONS[self.__resolution])
            filename = self.clear_filename(download.title, file_suffix)
            row = ','.join([filename, save_location, url, str(only_audio),
                            datetime.datetime.now().strftime('%m/%d/%Y %H:%M')]) + '\n'
            stream.download(filename=filename, output_path=save_location)
            return row
        except Exception as e:
            self.__error = True
            if on_error_tries == 0:
                self.__errors_list.append((e, url))
                return ''
            else:
                return self.__get_video_iitag(url, save_location, file_suffix, only_audio, on_error_tries - 1)

    def start(self, url: str, save_location: str, resolution: str, sender: Connection, only_audio: bool = False):
        file_suffix = 'mp4'
        log_list = []
        self.__current_attempt = 0
        self.__url = url
        self.__conn_sender = sender
        self.__resolution = resolution
        self.__only_audio = only_audio
        match self.__resolution:
            case 'Highest resolution' | 'Lowest resolution':
                video_getter = self.__get_video
            case _:
                video_getter = self.__get_video_iitag
        self.__save_location = save_location
        if url.startswith('https://www.youtube.com/watch'):
            try:
                self.__current_downloaded = url
                self.__playlist_len = 1
                res = video_getter(url=url, save_location=save_location, file_suffix=file_suffix, only_audio=only_audio,
                                   on_error_tries=self.__on_error_tries)
                if res:
                    log_list.append(res)
            except Exception as e:
                self.__error = True
                self.__playlist_index = 0
                self.__playlist_len = 0
                self.__handle_error(e, 0, [])
        elif url.startswith('https://www.youtube.com/playlist'):
            try:
                playlist = Playlist(url=url)
                self.__playlist_index = playlist.length
                self.__playlist_len = playlist.length
                for i, nxt_url in enumerate(playlist.video_urls):
                    self.__current_downloaded = nxt_url
                    self.__playlist_index -= 1
                    res = video_getter(url=nxt_url, save_location=save_location, file_suffix=file_suffix,
                                       only_audio=only_audio, on_error_tries=self.__on_error_tries)
                    if res:
                        log_list.append(res)
            except Exception as e:
                self.__error = True
                self.__playlist_index = 0
                self.__playlist_len = 0
                self.__handle_error(e, 0, [])
        log_from_error = []
        if self.__errors_list:
            log_from_error = self.__restart_on_error(video_getter=video_getter,
                                                     url_list=[nxt[1] for nxt in self.__errors_list],
                                                     save_location=save_location, file_suffix=file_suffix,
                                                     only_audio=only_audio)
            if self.__errors_list:
                error = ''
                tmp_list = []
                file_names = []
                for i, tmp in enumerate(self.__errors_list):
                    file_names.append(tmp[1])
                    if tmp[0] not in tmp_list:
                        tmp_list.append(tmp[0])
                        separate = ', ' if len(self.__errors_list)-1 > i else ''
                        error += f'{tmp[0]}{separate}'
                self.__handle_error(error, len(self.__errors_list), file_names)
        for nxt in log_from_error:
            log_list.append(nxt)
        send_data = {'state': None, 'log_list': log_list}
        self.__conn_sender.send(send_data)
        pass

    def __restart_on_error(self, video_getter: Callable, url_list: list[str], save_location: str, file_suffix: str, only_audio: bool = False) -> list:
        log_list = []
        tmp_error = []
        self.__playlist_index = len(url_list)
        self.__playlist_len = len(url_list)
        for url in url_list:
            self.__errors_list = []
            self.__current_downloaded = url
            self.__playlist_index -= 1
            for attempt in range(self.__error_download_attempts):
                self.__error_reload = f' reload attempt: {attempt + 1}'
                res = video_getter(url=url, save_location=save_location, file_suffix=file_suffix, only_audio=only_audio)
                if res:
                    log_list.append(res)
                    self.__errors_list = []
                    break
            if self.__errors_list:
                tmp_error.append(self.__errors_list[0])
        self.__errors_list = tmp_error
        return log_list
        pass

    def __on_complete_inner(self, *args):
        if self.__playlist_index == 0:
            self.__playlist_index = 0
            self.__playlist_len = 0
            self.__on_complete(*args)
        pass
    #-------------------------------------------------------------------------------------------------

    def __in_progress(self, *args):
        progress = float(1) - float(args[-1] / args[0].filesize)
        send_data = {'state': 'in_progress', 'progress': progress, 'button_state': 'disabled',
                     'file_count_info': f'File Nº - {self.download_index}',
                     'current_downloaded': self.__current_downloaded, 'download_index': self.download_index}
        self.__conn_sender.send(send_data)
        pass

    def __on_complete(self, *args):
        send_data = {'state': 'end', 'progress': 1.0, 'button_state': 'normal',
                     'file_count_info': 'Download Complete',
                     'current_downloaded': self.__save_location, 'download_index': self.download_index}
        self.__conn_sender.send(send_data)
        pass

    def __handle_error(self, *args):
        send_data = {'state': 'error', 'progress': 0.0, 'button_state': 'normal',
                     'file_count_info': 'Something went wrong, try again',
                     'current_downloaded': '', 'download_index': self.download_index, 'exception': args[0],
                     'bad_links': args[1], 'bad_file_names': args[2]}
        self.__conn_sender.send(send_data)
        pass


    pass