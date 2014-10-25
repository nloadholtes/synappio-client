import time
import heapq
import logging
import threading
from collections import deque


import zmq


log = logging.getLogger(__name__)


class Key(object):

    def __init__(self, public, secret=None):
        self.public = public
        self.secret = secret

    @classmethod
    def generate(cls):
        public, secret = zmq.curve_keypair()
        return cls(public, secret)

    def apply(self, socket):
        socket.curve_publickey = self.public
        socket.curve_secretkey = self.secret


class Worker(threading.Thread):

    def __init__(self, ctx, uri, handler, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.ctx = ctx
        self.uri = uri
        self.handler = handler

    def run(self):
        log.debug('Connect to %s', self.uri)
        socket = self.ctx.socket(zmq.REQ)
        socket.identity = self.getName()
        socket.connect(self.uri)
        socket.send_multipart(['READY'])
        try:
            while True:
                msg = socket.recv_multipart()
                log.debug('Recv: %s', msg)
                address, empty, request = msg
                assert empty == ''
                resp = self.handler(request)
                socket.send_multipart([address, '', resp])
        except zmq.ContextTerminated:
            return


class LoadBalancer(threading.Thread):

    def __init__(self, ctx, frontend_uri, backend_uri, *args, **kwargs):
        self.ctx = ctx
        self.frontend_uri = frontend_uri
        self.backend_uri = backend_uri
        self.backend_timeout = kwargs.pop('backend_timeout', None)
        super(LoadBalancer, self).__init__(*args, **kwargs)

    def frontend_socket(self):
        log.debug('Frontend: bind to %s', self.frontend_uri)
        socket = self.ctx.socket(zmq.ROUTER)
        socket.bind(self.frontend_uri)
        return socket

    def backend_socket(self):
        log.debug('Backend: bind to %s', self.backend_uri)
        socket = self.ctx.socket(zmq.ROUTER)
        socket.bind(self.backend_uri)
        return socket

    def run(self):
        frontend = self.frontend_socket()
        backend = self.backend_socket()
        reactor = TimeoutReactor(frontend, backend, self.backend_timeout)
        reactor.run()


class SecureBackendLoadBalancer(LoadBalancer):
    '''Same as load balancer, but uses crypto for backend'''

    def __init__(self, ctx, key, *args, **kwargs):
        super(SecureBackendLoadBalancer, self).__init__(
            ctx, *args, **kwargs)
        self.key = key

    def backend_socket(self):
        log.debug('Backend: bind to %s', self.backend_uri)
        socket = self.ctx.socket(zmq.ROUTER)
        self.key.apply(socket)
        socket.curve_server = True
        socket.bind(self.backend_uri)
        return socket


class SecureProxy(threading.Thread):
    '''Client to an insecure LB, worker to a secure LB'''

    def __init__(self, ctx, upstream_key, upstream_uri, downstream_uri,
            *args, **kwargs):
        self.ctx = ctx
        self.upstream_key = upstream_key
        self.upstream_uri = upstream_uri
        self.downstream_uri = downstream_uri
        self.identity = kwargs.pop('identity', '-')
        super(SecureProxy, self).__init__(*args, **kwargs)

    def upstream_socket(self):
        log.debug('Upstream: connect to %s', self.upstream_uri)
        socket = self.ctx.socket(zmq.REQ)
        if self.identity != '-':
            socket.identity = self.identity
        client_key = Key.generate()
        client_key.apply(socket)
        socket.curve_serverkey = self.upstream_key.public
        socket.connect(self.upstream_uri)
        return socket

    def downstream_socket(self):
        log.debug('Downstream: connect to %s', self.downstream_uri)
        socket = self.ctx.socket(zmq.REQ)
        socket.connect(self.downstream_uri)
        return socket

    def run(self):
        upstream = self.upstream_socket()
        downstream = self.downstream_socket()
        upstream.send('READY')
        try:
            while True:
                msg = upstream.recv_multipart()
                log.debug('Upstream: %s', msg)
                address, empty, request = msg
                downstream.send(request)
                response = downstream.recv()
                log.debug('Downstream: %s', msg)
                upstream.send_multipart([address, '', response])
        except zmq.ContextTerminated:
            return


class TimeoutReactor(object):

    def __init__(self, frontend, backend, timeout):
        self.frontend = frontend
        self.backend = backend
        self.timeout = timeout
        self.available = deque()
        self.busy = {}      # busy[worker_id] = req_id
        self.requests = {}  # requests[req_id] = (worker, (client, '', req))
        self.timeouts = []  # heap of (expires, req_id)
        self.request_id = 0

    def run(self):
        poller = zmq.Poller()
        poller.register(self.frontend, zmq.POLLIN)
        poller.register(self.backend, zmq.POLLIN)

        try:
            while True:
                timeout = self.poll_timeout()
                log.debug('Polling with timeout of %s', timeout)
                socks = dict(poller.poll(timeout))
                if self.backend in socks and socks[self.backend] == zmq.POLLIN:
                    self.handle_backend(self.backend.recv_multipart())
                self.handle_timeouts()
                if (self.available
                        and self.frontend in socks
                        and socks[self.frontend] == zmq.POLLIN):
                    self.handle_frontend(self.frontend.recv_multipart())
        except zmq.ContextTerminated:
            return

    def poll_timeout(self):
        if not self.timeouts:
            return None
        expires, req_id = self.timeouts[0]
        now = time.time()
        if expires < now:
            return None
        return (expires - now) * 1000

    def handle_backend(self, msg):
        log.debug("Backend: %s", msg)
        worker_addr, empty, client_addr = msg[:3]
        assert empty == ''
        self.available.appendleft(worker_addr)
        if client_addr == 'READY':
            return
        # Ack the req
        req_id = self.busy.pop(worker_addr, None)
        request = self.requests.pop(req_id, None)
        log.debug("... req_id = %s", req_id)
        if request is None:
            # Someone else handled this
            return
        # Handle the reply
        empty, reply = msg[3:]
        assert empty == ''
        self.frontend.send_multipart([client_addr, '', reply])

    def handle_frontend(self, msg, req_id=None):
        log.debug("Frontend: %s", msg)
        worker_addr = self.available.pop()
        log.debug("... route to %r", worker_addr)
        if req_id is None:
            req_id = self.request_id
            self.request_id += 1
        self.busy[worker_addr] = req_id
        self.requests[req_id] = (worker_addr, msg)
        if self.timeout is not None:
            expires = time.time() + self.timeout
            heapq.heappush(self.timeouts, (expires, req_id))
        self.backend.send_multipart([worker_addr, ''] + msg)

    def handle_timeouts(self):
        while self.available and self.timeouts:
            expires, req_id = self.timeouts[0]
            if expires > time.time():
                break
            heapq.heappop(self.timeouts)
            old_worker_addr, msg = self.requests.pop(req_id, (None, None))
            if old_worker_addr is None:
                # request was handled successfully
                continue
            log.debug('Timeout req %s', req_id)
            self.handle_frontend(msg, req_id)
