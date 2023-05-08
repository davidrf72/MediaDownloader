import multiprocessing

from Utils.Windows.treaded_main_window import MainWindow

multiprocessing.freeze_support()
if __name__ == '__main__':
    root = MainWindow(fg_color='darkblue')

