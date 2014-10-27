import logging

from .worker import MajorDomoWorker
from .client import MajorDomoClient

log = logging.getLogger(__name__)

class MajorDomoProxy(object):

    def __init__(self, uri_upstream, uri_downstream, service, **kwargs):
        self.worker = MajorDomoWorker(uri_upstream, service, self.target)
        self.client = MajorDomoClient(uri_downstream)
        self.service = service

    def serve_forever(self, context=None):
        for x in self.reactor(context):
            pass

    def reactor(self, context=None):
        for poller in self.worker.reactor():
            yield poller

    def target(self, *body):
        log.debug('Upstream req\n%r', body)
        result = self.client.send(self.service, *body)
        log.debug('Downstream reply\n%r', body)
        return result


