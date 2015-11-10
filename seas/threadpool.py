import sys
import time
import threading
from Queue import Queue, Empty


class Request(object):

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._event = threading.Event()
        self._success = None
        self._result = None

    def run(self):
        try:
            self._result = self._func(*self._args, **self._kwargs)
            self._success = True
        except Exception:
            self._result = sys.exc_info()
            self._success = False
        self._event.set()

    def wait(self, *args, **kwargs):
        self._event.wait(*args, **kwargs)

    def get(self):
        self.wait()
        if self._success:
            return self._result
        else:
            raise self._result[0], self._result[1], self._result[2]


class ThreadPool(object):

    def __init__(self, size, qsize=None):
        self.size = size
        self.q = Queue(maxsize=qsize)
        self.quitting = False
        self.threads = []
        self._local = threading.local()

    def init_local(self):
        '''Create thread-local variables here'''
        pass

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

    def request(self, func, *args, **kwargs):
        req = Request(func, *args, **kwargs)
        self.q.put(req)
        return req

    def worker(self):
        self.init_local()
        while not self.quitting:
            try:
                req = self.q.get(True, 1)
                req.run()
            except Empty:
                pass


def main():
    pool = ThreadPool(16)

    def func(i):
        print 'In func(%s)' % i
        time.sleep(1)
        print 'Leave func(%s)' % i
        return i
    results = [pool.put(func, i) for i in range(256)]
    pool.start()
    for r in results:
        print 'Result is %s' % r.get()
        sys.stdout.flush()
    pool.stop()

if __name__ == '__main__':
    main()
