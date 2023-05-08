import json
from tkinter import messagebox

from Utils.constants.constants import *


class Settings:
    def __init__(self, conf_file: str, defaults: dict):
        if not USER_DATA.exists():
            pathlib.Path.mkdir(USER_DATA)
        if not USER_WORK_DATA.exists():
            pathlib.Path.mkdir(USER_WORK_DATA)
        if not USER_WORK_FILE_PATH.exists():
            with open(USER_WORK_FILE_PATH, 'w', encoding='utf-8') as file:
                file.write(','.join(USER_WORK_FILE_HEADER) + '\n')
        self.__conf_file_path = USER_DATA.joinpath(conf_file)
        self.__defaults = defaults
        pass

    def read_config(self):
        if not self.__conf_file_path.exists():
            res = self.write_config(self.__defaults)
            if res is not None:
                messagebox.showerror(title='An Error', message=f'An error is: {res}')
            return self.__defaults
        try:
            with open(self.__conf_file_path, 'r', encoding='utf-8') as file:
                conf_data = json.load(file)
            return conf_data
        except Exception as e:
            return self.__defaults
        pass

    def write_config(self, conf_data: dict):
        try:
            with open(self.__conf_file_path, 'w', encoding='utf-8') as file:
                json.dump(conf_data, file)
        except Exception as e:
            return e
        return None
        pass
    pass