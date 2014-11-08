import logging

import zmq

from seas.zutil import zutil

from . import constants as MDP
from . import err


log = logging.getLogger(__name__)


class MajorDomoClient(object):

    def __init__(self, uri, timeout=None, retries=3, context=None):
        '''Create a client for the MDP.

        Required parameter:

            - uri: the URI of the broker

        Optional parameters:

            - timeout=None: how long to wait for a response before retrying
            - retries=3: how many times to attempt a request before giving up
              and raising err.MaxRetryError
            - context=None: zmq.Context to use

        '''
        self._uri = uri
        if timeout is None:
            self._timeout_ms = None
        else:
            self._timeout_ms = int(1000 * timeout)
        self._retries = retries
        if context is None:
            context = zmq.Context.instance()
        self._context = context
        self._socket = None
        self._poller = zmq.Poller()
        self._message = None
        self.reconnect()

    def send(self, service, *body):
        self.send_async(service, *body)
        return self.recv()

    def send_async(self, service, *body):
        self._message = [MDP.C_CLIENT, service] + list(body)
        self._socket.send_multipart(self._message)

    def recv(self):
        retries = self._retries
        while True:
            items = self._poller.poll(self._timeout_ms)
            if items:
                msg = self._socket.recv_multipart()
                assert msg[:2] == self._message[:2]     # service must match request
                self._message = None
                return msg[2:]
            elif retries:
                log.debug('timeout, reconnect')
                self._reconnect()
                self._socket.send_multipart(self._message)
                retries -= 1
            else:
                raise err.MaxRetryError()

    def destroy(self):
        if self._socket:
            self._poller.unregister(self._socket)
            self._socket.close()

    def _reconnect(self):
        if self._socket:
            self._poller.unregister(self._socket)
            self._socket.close()
        self._socket = self._make_socket(zmq.REQ)
        self._socket.connect(self._uri)
        self._poller.register(self._socket, zmq.POLLIN)

    def _make_socket(self, socktype):
        socket = self._context.socket(socktype)
        socket.linger = 0
        return socket


class SecureMajorDomoClient(zutil.SecureClient, MajorDomoClient):

    def __init__(self, server_key, client_key, *args, **kwargs):
        zutil.SecureClient.__init__(self, server_key, client_key)
        MajorDomoClient.__init__(self, *args, **kwargs)
