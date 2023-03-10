from Utils.main_window import MainWindow
import Utils.backend as backend


if __name__ == '__main__':
    root = MainWindow(backend=backend.get_video, fg_color='darkblue')

