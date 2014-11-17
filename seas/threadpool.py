import sys
import time
import threading
from Queue import Queue, Empty


class Result(object):

    def __init__(self, success, value):
        self._success = success
        self._value = value

    @classmethod
    def success(cls, value):
        return cls(True, value)

    @classmethod
    def failure(cls, ex_type, ex_value, ex_traceback):
        return cls(False, (ex_type, ex_value, ex_traceback))

    def get(self):
        if self._success:
            return self._value
        else:
            raise self._value[0], self._value[1], self._value[2]


class ThreadPool(object):

    def __init__(self, size):
        self.size = size
        self.qi = Queue()
        self.qo = Queue()
        self.quitting = False
        self.threads = []

    def start(self):
        self.threads = [
            threading.Thread(target=self.worker) for i in range(self.size)]
        for t in self.threads:
            t.setDaemon(True)
            t.start()

    def stop(self):
        self.quitting = True
        for t in self.threads:
            t.join()

    def put_job(self, func, *args, **kwargs):
        self.qi.put((func, args, kwargs))

    def get_result(self, *args, **kwargs):
        result = self.qo.get(*args, **kwargs)
        return result.get()

    def worker(self):
        while not self.quitting:
            try:
                (func, args, kwargs) = self.qi.get(True, 1)
                try:
                    result = func(*args, **kwargs)
                    self.qo.put(Result.success(result))
                except Exception:
                    self.qo.put(Result.failure(*sys.exc_info()))
            except Empty:
                pass


def main():
    pool = ThreadPool(16)

    def func(i):
        print 'In func(%s)' % i
        time.sleep(1)
        print 'Leave func(%s)' % i
        return i
    for i in range(256):
        pool.put_job(func, i)
    pool.start()
    for i in range(256):
        print 'Result is %s' % pool.get_result()
        sys.stdout.flush()
    pool.stop()

if __name__ == '__main__':
    main()
