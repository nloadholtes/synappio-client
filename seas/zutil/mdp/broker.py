import time
import logging
from collections import deque

import zmq

from . import constants as MDP
from . import err


log = logging.getLogger(__name__)


class MajorDomoBroker(object):

    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.poll_interval = kwargs.pop('poll_interval', 1.0)
        self.heartbeat_interval = kwargs.pop('heartbeat_interval', 1.0)
        self.heartbeat_interval = kwargs.pop('heartbeat_interval', 1.0)
        self.heartbeat_liveness = kwargs.pop('heartbeat_liveness', 3)
        self.socket = None
        self._control_uri = 'inproc://mdp-broker-{}'.format(id(self))
        self._services = {}
        self._workers = {}
        self._workers_ready = deque()

    def serve_forever(self, context=None):
        if context is None:
            context = zmq.Context.instance()
        for x in self.reactor(context):
            pass

    def reactor(self, context=None):
        if context is None:
            context = zmq.Context.instance()
        log.debug('In reactor %s', self._control_uri)
        self.socket = self.make_socket(context, zmq.ROUTER)
        control = self.make_socket(context, zmq.PULL)
        self.socket.bind(self.uri)
        control.bind(self._control_uri)
        self.poller = zmq.Poller()
        self.poller.register(control, zmq.POLLIN)
        self.poller.register(self.socket, zmq.POLLIN)

        while True:
            yield self.poller
            socks = dict(self.poller.poll(self.poll_interval))
            if control in socks:
                msg = control.recv()
                log.debug('control: %s', msg)
                if msg == 'TERMINATE':
                    log.debug('Terminating reactor')
                    control.close()
                    self.socket.close()
                    self.socket = None
                    break
            if self.socket in socks:
                msg = self.socket.recv_multipart()
                log.debug('recv:\n%r', msg)
                self.handle_message(list(reversed(msg)))

    def make_socket(self, context, socktype):
        socket = context.socket(socktype)
        socket.linger = 0
        return socket

    def handle_message(self, rmsg):
        sender_addr = rmsg.pop()
        assert rmsg.pop() == ''
        magic = rmsg.pop()
        if magic == MDP.C_CLIENT:
            self.handle_client(sender_addr, rmsg)
        elif magic == MDP.W_WORKER:
            self.handle_worker(sender_addr, rmsg)
        else:
            raise err.UnknownMagic(magic)

    def handle_client(self, sender_addr, rmsg):
        service_name = rmsg.pop()
        service = self.require_service(service_name)
        service.handle_client(sender_addr, rmsg)

    def handle_worker(self, sender_addr, rmsg):
        command = rmsg.pop()
        if command == MDP.W_READY:
            worker = self.require_worker(sender_addr)
            service = self.require_service(rmsg.pop())
            worker.register(service)
            worker.ready()
        else:
            raise NotImplementedError()

    def stop(self, context=None):
        if context is None:
            context = zmq.Context.instance()
        if self.socket:
            log.debug('Send TERMINATE to %s', self._control_uri)
            sock = self.make_socket(context, zmq.PUSH)
            sock.connect(self._control_uri)
            sock.send('TERMINATE')
            sock.close()

    def destroy(self):
        if self.socket:
            self.socket.close()

    def require_service(self, service_name):
        service = self._services.get(service_name)
        if service is None:
            service = Service(self, service_name)
            self._services[service_name] = service
        return service

    def require_worker(self, worker_addr):
        worker = self._workers.get(worker_addr)
        if worker is None:
            lifetime = self.heartbeat_interval * self.heartbeat_liveness
            worker = Worker(self, worker_addr, lifetime)
            self._workers[worker_addr] = worker
        return worker


class Worker(object):

    def __init__(self, broker, addr, lifetime):
        self.broker = broker
        self.addr = addr
        self.expires = time.time() + lifetime
        self.service = None

    def register(self, service):
        if self.service:
            log.debug('Worker already registered for %s', self.service.name)
            self.delete(True)
        self.service = service

    def ready(self):
        self.broker._workers_ready.appendleft(self)
        self.service.workers.appendleft(self)

    def delete(self, disconnect):
        if disconnect:
            self._broker.send(self.addr, '', MDP.W_WORKER, MDP.W_DISCONNECT)
        if self.service is not None:
            self.service.workers.remove(self)
        self.broker.workers.pop(self.addr)


class Service(object):

    def __init__(self, broker, name):
        self.broker = broker
        self.name = name
        self.requests = deque()     # (time, sender, body)
        self.workers = deque()      # workers available

    def handle_client(self, client_addr, rmsg):
        if self.workers:
            worker = self.workers.pop()
            log.debug('route request from %s to %s', client_addr, worker)
            worker.handle_client(client_addr, rmsg)
        else:
            log.debug('queueing request from %s', client_addr)
            self.requests.appendleft((time.time(), client_addr, rmsg))

