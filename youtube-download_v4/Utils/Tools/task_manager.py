from threading import Thread, Lock
from time import sleep

from Utils.Tools.downloader import Downloader
from Utils.Tools.facebook_downloader import FaceBookDownloader

class TaskManager(Thread):
    def __init__(self, allowed_task_count: int = 2, time_out: int = 2, after: int = 60):
        super(TaskManager, self).__init__()
        self.daemon = True
        self.__task_que: list[(Downloader | FaceBookDownloader, list)] = []
        self.__allowed_task_count = allowed_task_count if isinstance(allowed_task_count, int) and allowed_task_count > 0 else 2
        self.__active_task_count = 0
        self.__after = after if isinstance(after, int) and after >= 30 else 30
        self.__task_count = 0
        self.__time_out = time_out if isinstance(time_out, int) and 0 < time_out < (self.__after/2) else 2
        self.__cur_time_out = self.__time_out
        self.__timer = 0
        self.__task_lock = Lock()
        pass

    @property
    def active_task_count(self):
        return self.__active_task_count
        pass

    @property
    def task_count(self):
        return len(self.__task_que)
    pass

    @property
    def allowed_task_count(self):
        return self.__allowed_task_count
        pass

    @allowed_task_count.setter
    def allowed_task_count(self, value: int):
        self.__allowed_task_count = value if isinstance(value, int) and value > 0 else 2
        pass

    def complete_task(self):
        self.__active_task_count -= 1
        self.__task_count -= 1
        pass

    @property
    def all_tasks(self):
        return self.__task_count
        pass

    def append_task(self, task: tuple[Downloader | FaceBookDownloader, list]):
        self.__task_que.append(task)
        self.__task_count += 1
        pass

    @property
    def after(self):
        return self.__after
        pass

    @after.setter
    def after(self, value: int):
        self.__after = value if isinstance(value, int) and value >= 30 else 30
        pass

    def run(self) -> None:
        while True:
            #print('working...!!!')
            #print(f'All tasks: {len(self.__task_que)}', f'Active tasks: {self.__active_task_count}')
            if self.__task_que and self.__active_task_count < self.__allowed_task_count:
                for i in range(self.__allowed_task_count - self.__active_task_count):
                    if not self.__task_que: break
                    current_task = self.__task_que.pop(0)
                    current_task[1].append(self.__task_lock)
                    Thread(target=current_task[0].start, args=current_task[1], daemon=True).start()
                    self.__active_task_count += 1
                    self.__timer = 0
                    self.__cur_time_out = self.__time_out
            self.__timer += self.__cur_time_out
            if self.__after < self.__timer < self.__after * 2:
                self.__cur_time_out = self.__time_out * 2
            elif self.__timer > self.__after * 2:
                self.__cur_time_out = self.__time_out * 3
            sleep(self.__cur_time_out)
            #print(f'Timer: {self.__timer} -- TimeOut: {self.__cur_time_out}')
            #print(f'All tasks: {len(self.__task_que)}', f'Active tasks: {self.__active_task_count}')
            #print()
            pass
        pass

    def start(self) -> None:
        return super().start()
    pass
