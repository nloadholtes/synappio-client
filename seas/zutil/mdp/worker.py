'''Usage: worker [options] <uri>

Run an echo worker.

Options:
    -h --help   show this help message and exit
'''
import time
import logging

import zmq
import docopt

from seas.zutil import zutil

from . import constants as MDP


log = logging.getLogger(__name__)
log_dump = logging.getLogger('seas.zutil.dump')
log_heartbeat = logging.getLogger(__name__ + '.heartbeat')


def main():
    logging.basicConfig(level=logging.DEBUG)
    log_dump.setLevel(logging.INFO)
    args = docopt.docopt(__doc__)
    worker = MajorDomoWorker(args['<uri>'], 'echo', echo)
    worker.serve_forever()

def echo(*args):
    return list(args)



class MajorDomoWorker(object):

    def __init__(self, uri, service, target, **kwargs):
        '''Create a worker for the MDP.

        Required parameters:

            - uri: the URI of the broker
            - service: the name of the service provided
            - target: the name of the function to call to handle
              service requests

        Optional:

            - poll_interval=1.0: how frequently (in s) to timeout the Poller
            - heartbeat_interval=1.0: how frequently to send/expect heartbeats
            - heartbeat_liveness=3: how many missed heartbeats mean the broker
              is dead and we need to reconnect?
            - reconnect_delay=2.5: how long should we wait before attempting
              to reconnect to the broker after it has missed too many heartbeats?
            - context=None: zmq.Context to use
        '''
        self._uri = uri
        self._service = service
        self._target = target
        self._poll_interval_ms = int(1000 * kwargs.pop('poll_interval', 1.0))
        self._heartbeat_interval = kwargs.pop('heartbeat_interval', 1.0)
        self._heartbeat_liveness = kwargs.pop('heartbeat_liveness', 3)
        self._reconnect_delay = kwargs.pop('reconnect_delay', 2.5)
        context = kwargs.pop('context', None)
        if context is None:
            context = zmq.Context.instance()
        self._context = context
        self._socket = None
        self._poller = zmq.Poller()
        self._broker_liveness = 0
        self._next_heartbeat = 0
        self._shutting_down = False

    def serve_forever(self):
        for x in self.reactor():
            pass

    def reactor(self):
        self._reconnect()
        while not self._shutting_down:
            yield self._poller
            socks = dict(self._poller.poll(self._poll_interval_ms))
            if self._socket in socks:
                msg = self._socket.recv_multipart()
                log_dump.debug('recv\n%r', msg)
                self._handle_message(list(reversed(msg)))
            else:
                self._handle_timeout()
            if time.time() > self._next_heartbeat:
                log_heartbeat.debug('send heartbeat')
                self._send(MDP.W_HEARTBEAT)
                self._next_heartbeat = time.time() + self._heartbeat_interval
        log.info('Terminating reactor')
        self._socket.close()
        self._socket = None

    def stop(self):
        self._shutting_down = True

    def destroy(self):
        if self._socket:
            self._socket.close()
            self._socket = None

    def _reconnect(self):
        """Connect or reconnect to broker"""
        if self._socket:
            self._poller.unregister(self._socket)
            self._socket.close()
        self._socket = self._make_socket(zmq.DEALER)
        self._socket.connect(self._uri)
        self._poller.register(self._socket, zmq.POLLIN)
        log.info('Connect to broker at %s', self._uri)
        self._send(MDP.W_READY, self._service)
        self._broker_liveness = self._heartbeat_liveness

    def _make_socket(self, socktype):
        socket = self._context.socket(socktype)
        socket.linger = 0
        return socket

    def _send(self, command, *parts):
        msg = ['', MDP.W_WORKER, command] + list(parts)
        log_dump.debug('send %r\n%r', command, msg)
        self._socket.send_multipart(msg)
        self._next_heartbeat = time.time() + self._heartbeat_interval

    def _handle_message(self, rmsg):
        self._broker_liveness = self._heartbeat_liveness
        assert '' == rmsg.pop()
        assert MDP.W_WORKER == rmsg.pop()
        command = rmsg.pop()
        if command == MDP.W_HEARTBEAT:
            log_heartbeat.debug('recv heartbeat')
            return
        elif command == MDP.W_DISCONNECT:
            self._reconnect()
        elif command == MDP.W_REQUEST:
            client = rmsg.pop()
            assert '' == rmsg.pop()
            args = list(reversed(rmsg))
            response = self._target(*args)
            self._send(MDP.W_REPLY, client, '', *response)
        else:
            log.error('Invalid command: %r', command)

    def _handle_timeout(self):
        self._broker_liveness -= 1
        if self._broker_liveness == 0:
            log.debug('Disconnected, retry in %ss', self._reconnect_delay)
            time.sleep(self._reconnect_delay)
            self._reconnect()


class SecureMajorDomoWorker(zutil.SecureClient, MajorDomoWorker):

    def __init__(self, server_key, client_key, *args, **kwargs):
        zutil.SecureClient.__init__(self, server_key, client_key)
        MajorDomoWorker.__init__(self, *args, **kwargs)


if __name__ == '__main__':
    main()


