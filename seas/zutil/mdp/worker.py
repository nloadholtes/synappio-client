import time
import logging

import zmq

from . import constants as MDP


log = logging.getLogger(__name__)
log_dump = logging.getLogger('seas.zutil.dump')
log_heartbeat = logging.getLogger(__name__ + '.heartbeat')


class MajorDomoWorker(object):

    def __init__(self, uri, service, target, **kwargs):
        self.uri = uri
        self.service = service
        self.target = target
        self.poll_interval = kwargs.pop('poll_interval', 1.0)
        self.heartbeat_interval = kwargs.pop('heartbeat_interval', 1.0)
        self.heartbeat_liveness = kwargs.pop('heartbeat_liveness', 3)
        self.reconnect_delay = kwargs.pop('reconnect_delay', 2.5)
        self._socket = None
        self._poller = zmq.Poller()
        self._cur_liveness = 0
        self._heartbeat_at = 0
        self._control_uri = 'inproc://mdp-worker-{}'.format(id(self))

    def serve_forever(self, context=None):
        if context is None:
            context = zmq.Context.instance()
        for x in self.reactor(context):
            pass

    def reactor(self, context=None):
        if context is None:
            context = zmq.Context.instance()
        control = context.socket(zmq.PULL)
        control.bind(self._control_uri)
        self._poller.register(control, zmq.POLLIN)
        self.reconnect(context)
        while True:
            yield self._poller
            socks = dict(self._poller.poll(1000 * self.poll_interval))
            if control in socks:
                msg = control.recv()
                log.info('control: %s', msg)
                if msg == 'TERMINATE':
                    log.info('Terminating reactor')
                    control.close()
                    self._socket.close()
                    self._socket = None
                    break
            elif self._socket in socks:
                msg = self._socket.recv_multipart()
                log_dump.debug('recv\n%r', msg)
                self._handle_message(context, msg)
            else:
                self._handle_timeout(context)
            if time.time() > self._heartbeat_at:
                log_heartbeat.info('send heartbeat')
                self._send(MDP.W_HEARTBEAT)
                self._heartbeat_at = time.time() + self.heartbeat_interval

    def stop(self, context=None):
        if context is None:
            context = zmq.Context.instance()
        if self._socket:
            log.info('Send TERMINATE to %s', self._control_uri)
            sock = self.make_socket(context, zmq.PUSH)
            sock.connect(self._control_uri)
            sock.send('TERMINATE')
            sock.close()

    def destroy(self):
        if self._socket:
            self._socket.close()

    def reconnect(self, context):
        """Connect or reconnect to broker"""
        if self._socket:
            self._poller.unregister(self._socket)
            self._socket.close()
        self._socket = self.make_socket(context, zmq.DEALER)
        self._socket.connect(self.uri)
        self._poller.register(self._socket, zmq.POLLIN)
        log.info('Connect to broker at %s', self.uri)
        self._send(MDP.W_READY, self.service)
        self._cur_liveness = self.heartbeat_liveness
        self._heartbeat_at = time.time() + self.heartbeat_interval

    def make_socket(self, context, socktype):
        socket = context.socket(socktype)
        socket.linger = 0
        return socket

    def _send(self, command, *parts):
        msg = ['', MDP.W_WORKER, command] + list(parts)
        log_dump.debug('send %r\n%r', command, msg)
        self._socket.send_multipart(msg)
        self._heartbeat_at = time.time() + self.heartbeat_interval

    def _handle_message(self, context, msg):
        self._cur_liveness = self.heartbeat_liveness
        assert len(msg) >= 3
        empty, magic, command = msg[:3]
        assert [empty, magic] == ['', MDP.W_WORKER]
        if command == MDP.W_HEARTBEAT:
            log_heartbeat.info('recv heartbeat')
            return
        elif command == MDP.W_DISCONNECT:
            self.reconnect(context)
        elif command == MDP.W_REQUEST:
            client, empty = msg[3:5]
            assert empty == ''
            response = self.target(*msg[5:])
            self._send(MDP.W_REPLY, client, empty, *response)
        else:
            log.error('Invalid message\n%r', msg)

    def _handle_timeout(self, context):
        self._cur_liveness -= 1
        if self._cur_liveness == 0:
            log.debug('Disconnected, retry')
            time.sleep(self.reconnect_delay)
            self.reconnect(context)


class SecureMajorDomoWorker(MajorDomoWorker):

    def __init__(self, server_key, client_key, *args, **kwargs):
        self.server_key = server_key
        self.client_key = client_key
        super(SecureMajorDomoWorker, self).__init__(*args, **kwargs)

    def make_socket(self, context, socktype):
        socket = super(SecureMajorDomoWorker, self).make_socket(context, socktype)
        self.client_key.apply(socket)
        socket.curve_serverkey = self.server_key.public
        return socket
