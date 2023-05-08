import os
from win10toast_click import ToastNotifier

class WinNotifier:
    def __init__(self):
        self.__note = ToastNotifier()
        pass

    def __open_url(self, url: str):
        if os.path.isfile(url):
            file_name = url if url.lower().endswith('mp4') else f'{url}.mp4'
        else:
            file_name = url
        os.startfile(file_name)
        pass

    def show(self, url: str, title: str, message: str, icon_path=None, duration=5, threaded=False):
        self.__note.show_toast(title=title, msg=message, icon_path=icon_path,
                               duration=duration, threaded=threaded,
                               callback_on_click=lambda: self.__open_url(url))
        pass
    pass

