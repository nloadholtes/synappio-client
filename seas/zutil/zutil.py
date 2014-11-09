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


class SecureClient(object):
    '''Mixin for providing a secure _make_socket method'''

    def __init__(self, server_key, client_key):
        '''Create a secure client using CURVE cryptography.

        Required parameters:

            - server_key: the server's (broker's) public zutil.Key
            - client_key: the client's private zutil.Key
        '''
        self._server_key = server_key
        self._client_key = client_key

    def _make_socket(self, socktype):
        socket = super(SecureClient, self).make_socket(socktype)
        self._client_key.apply(socket)
        socket._curve_serverkey = self.server_key.public
        return socket


class SecureServer(object):
    '''Mixin for providing a secure _make_socket method'''

    def __init__(self, key, context=None):
        '''Create a secure client using CURVE cryptography.

        Required parameter:

            - key: the server's private zutil.Key
        '''
        self._key = key

    def _make_socket(self, socktype):
        socket = super(SecureServer, self).make_socket(socktype)
        self._key.apply(socket)
        socket.curve_server = True
        return socket


class MaxRetryError(Exception):
    pass


class MDP(object):
    W_READY = '\x01'
    W_REQUEST = '\x02'
    W_REPLY = '\x03'
    W_HEARTBEAT = '\x04'
    W_DISCONNECT = '\x05'
    W_WORKER = 'MDPW01'
    C_CLIENT = 'MDPC01'


class MajorDomoClient(object):

    def __init__(self, uri, timeout, retries=3, context=None):
        self.uri = uri
        self.timeout = timeout
        if context is None:
            context = zmq.Context.instance()
        self.context = context
        self.socket = None
        self.poller = zmq.Poller()
        self.reconnect()

    def reconnect(self):
        if self.socket:
            self.poller.unregister(self.socket)
            self.socket.close()
        self.socket = self.ctx.socket(zmq.REQ)
        self.socket.linger = 0
        self.socket.connect(self.broker)
        self.poller.register(self.socket, zmq.POLLIN)

    def send(self, service, request):
        if not isinstance(request, list):
            request = [request]
        request = [MDP.C_CLIENT, service] + request
        log.debug('send request to %r service\n%r', service, request)

        retries = self.retries
        while retries > 0:
            self.socket.send_multipart(request)
            items = self.poller.poll(self.timeout)
            if items:
                msg = self.client.recv_multipart()
                log.debug('recv reply\n%r', msg)
                assert len(msg) >= 3
                assert msg[:2] == [MDP.C_CLIENT, service]
                return msg[2]
            elif retries:
                log.debug('timeout, reconnect')
                self.reconnect()
                retries -= 1
            else:
                log.debug('timeout, retries exhausted')
                raise MaxRetryError()


class MajorDomoWorker(threading.Thread):

    def __init__(self, uri, service, target, *args, **kwargs):
        self.uri = uri
        self.service = service
        self.target = target
        self.heartbeat_delay = kwargs.pop('heartbeat_delay', 2.5)
        self.heartbeat_liveness = kwargs.pop('heartbeat_liveness', 3)
        self.reconnect_delay = kwargs.pop('reconnect_delay', 2.5)
        self.poller_timeout = kwargs.pop('poller_timeout', 2.5)
        context = kwargs.pop('context', None)
        if context is None:
            context = zmq.Context.instance()
        self.context = context
        super(MajorDomoWorker, self).__init__(*args, **kwargs)
        self._socket = None
        self._poller = zmq.Poller()
        self._cur_liveness = 0
        self._heartbeat_at = 0

    def _reconnect(self):
        """Connect or reconnect to broker"""
        if self._socket:
            self._poller.unregister(self._socket)
            self._socket.close()
        self._socket = self.ctx._socket(zmq.DEALER)
        self._socket.linger = 0
        self._socket.connect(self.uri)
        self._poller.register(self._socket, zmq.POLLIN)
        log.debug('Connect to broker at %s', self.uri)
        self._send(MDP.W_READY, self.service)
        self._cur_liveness = self.liveness
        self._heartbeat_at = time.time() + self.timeout

    def _send(self, command, *parts):
        msg = ['', MDP.W_WORKER, command] + list(parts)
        log.debug('send %r\n%r', command, msg)
        self._socket.send_multipart(msg)
        self._heartbeat_at = time.time() + self.timeout

    def run(self):
        self._reconnect()
        while True:
            items = self.poller.poll(self.timeout)
            if items:
                msg = self.worker.recv_multipart()
                log.debug('recv\n%r', msg)
                self._handle_message(msg)
            else:
                self._handle_timeout()
            if time.time() > self._heartbeat_at:
                self._send(MDP.W_HEARTBEAT)
                self.heartbeat_at = time.time() + self.heartbeat

    def _handle_message(self, msg):
        self._cur_liveness = self.heartbeat_liveness
        assert len(msg) >= 3
        empty, magic, command = msg[:3]
        assert [empty, magic] == ['', MDP.W_WORKER]
        if command == MDP.W_HEARTEAT:
            pass
        elif command == MDP.W_DISCONNECT:
            self._reconnect()
        elif command == MDP.W_REQUEST:
            client, empty = msg[3:5]
            assert empty == ''
            response = self.target(*msg[5:])
            self._send(MDP.W_REPLY, client, empty, *response)
        elif command == MDP.W_HEARTEAT:
            pass
        else:
            log.error('Invalid message\n%r', msg)

    def _handle_timeout(self):
        self._cur_liveness -= 1
        if self._cur_liveness == 0:
            log.debug('Disconnected, retry')
            time.sleep(self.reconnect_delay)
            self._reconnect()


class LazyPirateClient(object):

    def __init__(self, ctx, uri, timeout, retries=3):
        self.ctx = ctx
        self.uri = uri
        self.timeout_ms = int(timeout * 1000)
        self.retries = retries
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect(uri)
        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)

    def send(self, request):
        for attempt in range(self.retries):
            self.socket.send(request)
            socks = dict(self.poll.poll(self.timeout_ms))
            if socks.get(self.socket) == zmq.POLLIN:
                reply = self.socket.recv()
                return reply
            else:
                log.info('timeout')
                self._bounce_socket()
        raise MaxRetryError('Tried {} times'.format(attempt))

    def send_multipart(self, request):
        for attempt in range(self.retries):
            self.socket.send_multipart(request)
            socks = dict(self.poll.poll(self.timeout_ms))
            if socks.get(self.socket) == zmq.POLLIN:
                reply = self.socket.recv_multipart()
                return reply
            else:
                self._bounce_socket()
        raise MaxRetryError('Tried {} times'.format(attempt))

    def _bounce_socket(self):
        # Socket is confused. Close and remove it.
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()
        self.poll.unregister(self.socket)
        # Create new connection
        self.socket = self.ctx.socket(zmq.REQ)
        self.socket.connect(self.uri)
        self.poll.register(self.socket, zmq.POLLIN)


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
