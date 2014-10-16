import time
import logging

import boto.sqs
from boto.sqs.message import RawMessage

log = logging.getLogger(__name__)


class Listener(object):

    def __init__(self, region, key, secret, queue):
        self.conn = boto.sqs.connect_to_region(
            region, aws_access_key_id=key, aws_secret_access_key=secret)
        self.queue = self.conn.get_queue(queue)
        self.queue.set_message_class(RawMessage)

    def handle(self, message):
        raise NotImplementedError()

    def run(self):
        while True:
            try:
                messages = self.queue.get_messages(8)
            except Exception:
                log.exception('Failed to GET from queue, wait 5s')
                time.sleep(5)
            for msg in messages:
                try:
                    self.handle(msg)
                except Exception:
                    log.exception('Error in handling message %s', msg)
