import datetime
import sys

import youtube_dl
from Utils.constants.constants import *
from contextlib import contextmanager
# https://www.facebook.com/watch?v=1004154427228761

class _FilenameCollectorPP(youtube_dl.postprocessor.common.PostProcessor):
    def __init__(self, on_complete, logging: bool = True):
        super(_FilenameCollectorPP, self).__init__(None)
        self.filenames = []
        self.__on_complete = on_complete
        self.__logging = logging
        pass

    def run(self, information):
        self.filenames.append(information['filepath'])
        self.__on_complete(self.__logging)
        return [], information
    pass


class _LoggerOutputs:
    def error(msg):
        print("Captured Error: "+msg)
        pass
    def warning(msg):
        print("Captured Warning: "+msg)
        pass
    def debug(msg):
        #print("Captured Log: "+msg)
        pass


class FaceBookDownloader:
    def __init__(self, in_progress, on_complete, handle_error):
        self.__in_progress = in_progress
        self.__on_complete = on_complete
        self.__handle_error = handle_error
        self.__filename_collector = None
        self.__playlist_index = 0
        self.__playlist_len = 0
        self.__save_location = ''
        self.__url = ''
        pass

    @property
    def download_index(self):
        return f'{1} from {1}'
        pass

    @staticmethod
    @contextmanager
    def suppress_stdout():
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            old_err = sys.stderr
            sys.stdout = devnull
            sys.stderr = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_err

    def start(self, url: str, save_location, logging: bool = True):
        try:
            # https://www.facebook.com/watch?v=1004154427228761
            # https://fb.watch/juJWcVqnbb/
            option = {'format': 'best/bestvideo+bestaudio', "quiet": True, "restrictfilenames": False, 'ignor_warnings': True, "logger": _LoggerOutputs, 'no_warnings': True, 'verbose': False} #"external_downloader_args": ['-loglevel', 'panic']}
            self.__filename_collector = _FilenameCollectorPP(self.__on_end, logging)
            self.__save_location = save_location
            self.__url = url

            os.chdir(save_location)
            with FaceBookDownloader.suppress_stdout():
                with youtube_dl.YoutubeDL(option) as u:
                    u.add_progress_hook(self.__progress)
                    u.add_post_processor(self.__filename_collector)
                    u.download([url])
        except:
            print("Invalid link or selected resolution unavailable!")
            self.__handle_error()
        pass

    def __progress(self, *args):
        self.__in_progress(*args)
        pass

    def __on_end(self, logging: bool = True):
        log_list = [','.join([self.__filename_collector.filenames[0], self.__save_location, self.__url, 'None', datetime.datetime.now().strftime('%m/%d/%Y %H:%M')]) + '\n']
        if logging and len(log_list) > 0:
            self.__write_log(log_list)
        self.__on_complete([None])
        pass

    def __write_log(self, rows: list):
        with open(USER_WORK_FILE_PATH, 'a', encoding='utf-8') as file:
            file.writelines(rows)
            pass
    pass
