import logging

import zmq

from . import constants as MDP
from . import err

log = logging.getLogger(__name__)

class MajorDomoClient(object):

    def __init__(self, uri, timeout=None, retries=3, context=None):
        self.uri = uri
        if timeout is None:
            self.timeout_ms = None
        else:
            self.timeout_ms = int(1000 * timeout)
        self.retries = retries
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
        self.socket = self.make_socket(self.context, zmq.REQ)
        self.socket.connect(self.uri)
        self.poller.register(self.socket, zmq.POLLIN)

    def make_socket(self, context, socktype):
        socket = context.socket(socktype)
        socket.linger = 0
        return socket

    def send(self, service, *body):
        req = _Request(self, service, *body)
        req.send()
        return req.recv()

    def send_async(self, service, *body):
        req = _Request(self, service, *body)
        req.send()
        return req

    def destroy(self, context=None):
        if self.socket:
            self.poller.unregister(self.socket)
            self.socket.close()


class SecureMajorDomoClient(MajorDomoClient):

    def __init__(self, server_key, client_key, *args, **kwargs):
        self.server_key = server_key
        self.client_key = client_key
        super(SecureMajorDomoClient, self).__init__(*args, **kwargs)

    def make_socket(self, context, socktype):
        socket = super(SecureMajorDomoClient, self).make_socket(context, socktype)
        self.client_key.apply(socket)
        socket.curve_serverkey = self.server_key.public
        return socket


class _Request(object):

    def __init__(self, client, service, *body):
        self.client = client
        self.service = service
        self.message = [MDP.C_CLIENT, service] + list(body)

    def send(self):
        log.debug('send %s', self.message)
        self.client.socket.send_multipart(self.message)

    def recv(self):
        retries = self.client.retries
        while True:
            items = self.client.poller.poll(self.client.timeout_ms)
            if items:
                msg = self.client.socket.recv_multipart()
                assert msg[:2] == [MDP.C_CLIENT, self.service]
                return msg[2:]
            elif retries:
                log.debug('timeout, reconnect')
                self.client.reconnect()
                self.send()
                retries -= 1
            else:
                raise err.MaxRetryError()



