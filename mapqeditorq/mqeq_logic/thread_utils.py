

import threading


class ExceptionRaisingThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.__exception = None

    def run(self):
        try:
            super().run()
        except Exception as e:
            self.__exception = e

    def join(self, timeout=None):
        super().join(timeout)
        if self.__exception is not None:
            raise self.__exception


