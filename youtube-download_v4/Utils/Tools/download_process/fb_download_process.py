import datetime
import sys
from multiprocessing.connection import Connection
import youtube_dl
from Utils.constants.constants import *
from contextlib import contextmanager
# https://www.facebook.com/watch?v=1004154427228761

class _FilenameCollectorPP(youtube_dl.postprocessor.common.PostProcessor):
    def __init__(self, on_complete):
        super(_FilenameCollectorPP, self).__init__(None)
        self.filenames = []
        self.__on_complete = on_complete
        pass

    def run(self, information):
        self.filenames.append(information['filepath'])
        self.__on_complete()
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


class FBDownloaderProcess:
    def __init__(self):
        self.__current_downloaded = ''
        self.__filename_collector = None
        self.__playlist_index = 0
        self.__playlist_len = 0
        self.__save_location = ''
        self.__url = ''
        self.__conn_sender = None
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

    def start(self, url: str, save_location, sender: Connection):
        self.__conn_sender = sender
        try:
            # https://www.facebook.com/watch?v=1004154427228761
            # https://fb.watch/juJWcVqnbb/
            option = {'format': 'best/bestvideo+bestaudio', "quiet": True, "restrictfilenames": False, 'ignor_warnings': True, "logger": _LoggerOutputs, 'no_warnings': True, 'verbose': False} #"external_downloader_args": ['-loglevel', 'panic']}
            self.__filename_collector = _FilenameCollectorPP(self.__on_end)
            self.__save_location = save_location
            self.__url = url

            os.chdir(save_location)
            self.__current_downloaded = url
            with FBDownloaderProcess.suppress_stdout():
                with youtube_dl.YoutubeDL(option) as u:
                    u.add_progress_hook(self.__progress)
                    u.add_post_processor(self.__filename_collector)
                    u.download([url])
        except Exception as e:
            #print("Invalid link or selected resolution unavailable!")
            self.__handle_error(e)
            send_data = {'state': None, 'progress': 0.0, 'button_state': 'normal',
                         'file_count_info': 'Something went wrong, try again',
                         'current_downloaded': self.__current_downloaded, 'log_list': [],
                         'download_index': self.download_index, 'exception': str(e)}
            self.__conn_sender.send(send_data)
        pass

    def __progress(self, *args):
        self.__in_progress(*args)
        pass

    def __on_end(self):
        log_list = [','.join([self.__filename_collector.filenames[0], self.__save_location, self.__url, 'None', datetime.datetime.now().strftime('%m/%d/%Y %H:%M')]) + '\n']

        send_data = {'state': None, 'progress': 1.0, 'button_state': 'normal',
                     'file_count_info': 'Download Complete',
                     'current_downloaded': self.__save_location, 'log_list': log_list,
                     'download_index': self.download_index}
        self.__conn_sender.send(send_data)
        pass
    # -------------------------------------------------------------------------------------------------
    def __in_progress(self, *args):
        progress = float(1) - float((args[0]['total_bytes']-args[0]['downloaded_bytes']) / args[0]['total_bytes'])
        send_data = {'state': 'in_progress', 'progress': progress, 'button_state': 'disabled',
                     'file_count_info': f'File Nº - {self.download_index}',
                     'current_downloaded': self.__current_downloaded, 'download_index': self.download_index}
        self.__conn_sender.send(send_data)
        pass

    def __handle_error(self, *args):
        send_data = {'state': 'error', 'progress': 0.0, 'button_state': 'normal',
                     'file_count_info': 'Something went wrong, try again',
                     'current_downloaded': '', 'download_index': self.download_index, 'exception': str(args[0])}
        self.__conn_sender.send(send_data)
        pass
    pass
