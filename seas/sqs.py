import time
import logging

log = logging.getLogger(__name__)


class Listener(object):

    def __init__(self, queue, handle=None):
        self.queue = queue
        if handle is not None:
            self.handle = handle

    def handle(self, message):
        raise NotImplementedError()

    def run(self):
        log.debug('Entering Listener.run')
        while True:
            try:
                messages = self.queue.get_messages(10, wait_time_seconds=10)
                log.debug('Got %d messages', len(messages))
            except Exception:
                log.exception('Failed to GET from queue, wait 5s')
                time.sleep(5)
                continue
            for msg in messages:
                log.debug('Got message %s', msg)
                try:
                    self.handle(msg)
                except Exception:
                    log.exception('Error in handling message %s', msg)
