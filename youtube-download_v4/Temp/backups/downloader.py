import datetime

from pytube import YouTube, request, Playlist
from Utils.constants.constants import *

request.default_range_size = 500000

class Downloader:
    def __init__(self, in_progress, on_complete, handle_error, resolution: str):
        self.__in_progress = in_progress
        self.__on_complete = on_complete
        self.__handle_error = handle_error
        self.__playlist_index = 0
        self.__playlist_len = 0
        self.__resolution = resolution
        pass

    @property
    def download_index(self):
        return f'{self.__playlist_len - self.__playlist_index} from {self.__playlist_len}'
        pass

    @staticmethod
    def clear_filename(file_name: str, file_ext: str = '') -> str:
        bad_symbols = r'!()[]{}@#$%^&*.?<>=+|\\/-~`:;"\''
        ext = file_name[-4:] if not file_ext else f'.{file_ext}'
        name = file_name[:-4] if not file_ext else file_name
        tmp_name = ''.join([sym for sym in name if sym not in bad_symbols])
        return f'{tmp_name}{ext}'
        pass

    def __get_video(self, url, save_location, file_suffix: str, only_audio: bool = False) -> str:
        try:
            download = YouTube(url, on_progress_callback=self.__in_progress, on_complete_callback=self.__on_complete_inner)
            if only_audio:
                stream = download.streams.filter(only_audio=True).first()
            else:
                stream = download.streams.filter(progressive=True).get_highest_resolution()
            filename = self.clear_filename(download.title, file_suffix)
            row = ','.join([filename, save_location, url, str(only_audio), datetime.datetime.now().strftime('%m/%d/%Y %H:%M')]) + '\n'
            stream.download(filename=filename, output_path=save_location)
            return row
        except:
            self.__error = True
            self.__playlist_index = 0
            self.__playlist_len = 0
            self.__handle_error()
            return ''

    def __get_video_iitag(self, url, save_location, file_suffix: str, only_audio: bool = False) -> str:
        try:
            download = YouTube(url, on_progress_callback=self.__in_progress, on_complete_callback=self.__on_complete_inner)
            if only_audio:
                stream = download.streams.filter(only_audio=True).first()
            else:
                stream = download.streams.get_by_itag(RESOLUTIONS[self.__resolution])
            filename = self.clear_filename(download.title, file_suffix)
            row = ','.join([filename, save_location, url, str(only_audio), datetime.datetime.now().strftime('%m/%d/%Y %H:%M')]) + '\n'
            stream.download(filename=filename, output_path=save_location)
            return row
        except:
            self.__error = True
            self.__playlist_index = 0
            self.__playlist_len = 0
            self.__handle_error()
            return ''

    def start(self, url: str, save_location, resolution: str, only_audio: bool = False, logging: bool = True):
        file_suffix = 'mp4'
        log_list = []
        self.__resolution = resolution
        match self.__resolution:
            case 'Highest resolution' | 'Lowest resolution':
                video_getter = self.__get_video
            case _:
                video_getter = self.__get_video_iitag

        if url.startswith('https://www.youtube.com/watch'):
            self.__playlist_len = 1
            res = video_getter(url=url, save_location=save_location, file_suffix=file_suffix, only_audio=only_audio)
            log_list.append(res)
        elif url.startswith('https://www.youtube.com/playlist'):
            try:
                playlist = Playlist(url=url)
                self.__playlist_index = playlist.length
                self.__playlist_len = playlist.length
                for i, nxt_url in enumerate(playlist.video_urls):
                    self.__playlist_index -= 1
                    res = video_getter(url=nxt_url, save_location=save_location, file_suffix=file_suffix, only_audio=only_audio)
                    log_list.append(res)
            except:
                self.__error = True
                self.__playlist_index = 0
                self.__playlist_len = 0
                self.__handle_error()
                return
        if logging and len(log_list) > 0:
            self.__write_log(log_list)

    @staticmethod
    def __write_log(rows: list):
        with open(USER_WORK_FILE_PATH, 'a', encoding='utf-8') as file:
            file.writelines(rows)
            pass
        pass

    def __on_complete_inner(self, *args):
        if self.__playlist_index == 0:
            self.__playlist_index = 0
            self.__playlist_len = 0
            self.__on_complete(*args)
        pass

    pass