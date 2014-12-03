'''Usage: broker [options] <uri>

Options:
    -h --help   show this help message and exit
'''
import time
import logging
from collections import deque
from binascii import hexlify

import zmq
import docopt

from seas.zutil import zutil
from seas.zutil.heartbeat import HeartbeatManager

from . import constants as MDP
from . import err


log = logging.getLogger(__name__)
log_dump = logging.getLogger('seas.zutil.dump')
log_heartbeat = logging.getLogger(__name__ + '.heartbeat')


def main():
    logging.basicConfig(level=logging.INFO)
    log_dump.setLevel(logging.INFO)
    args = docopt.docopt(__doc__)
    broker = MajorDomoBroker(args['<uri>'])
    broker.serve_forever()


class MajorDomoBroker(object):

    def __init__(self, uri, **kwargs):
        '''Create a broker for the MDP.

        Required parameter:

            - uri: the URI to bind (e.g. tcp://*:9200)

        Optional parameters:

            - request_timeout=60: how long (in s) before we discard a request
              which has not been served by some worker?
            - poll_interval=1.0: how frequently (in s) to timeout the Poller
            - heartbeat_interval=1.0: how frequently to send/expect heartbeats
            - heartbeat_liveness=3: how many missed heartbeats mean the worker
              is dead and we need to disconnect it?
            - context=None: zmq.Context to use
        '''
        self._uri = uri
        self._poll_interval_ms = int(1000 * kwargs.pop('poll_interval', 1.0))
        self._request_timeout = kwargs.pop('request_timeout', 60)
        self.heartbeat = HeartbeatManager(
            kwargs.pop('heartbeat_interval', 1.0),
            kwargs.pop('heartbeat_liveness', 3))
        self._context = kwargs.pop('context', None)
        if self._context is None:
            self._context = zmq.Context.instance()
        self._socket = None
        self._services = {}
        self._workers = {}
        self._shutting_down = False

    def serve_forever(self):
        for x in self.reactor():
            log.debug('Services:')
            for name, svc in self._services.items():
                log.debug('%s: %s', name, svc)
            log.debug('Workers:')
            for name, worker in self._workers.items():
                log.debug('%s: %s', name, worker)
            log.debug('---')


    def reactor(self):
        log.debug('In reactor')
        self._socket = self._make_socket(zmq.ROUTER)
        self._socket.bind(self._uri)
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        while not self._shutting_down:
            yield poller
            try:
                socks = dict(poller.poll(self._poll_interval_ms))
                if self._socket in socks:
                    msg = self._socket.recv_multipart()
                    log_dump.debug('recv:\n%r', msg)
                    try:
                        self._handle_message(list(reversed(msg)))
                    except Exception:
                        log.exception('Error handling message:\n%r', msg)

                self._send_heartbeats()
                self._reap_workers()
            except AssertionError as err:
                log.exception('Error in reactor')

        log.info('Terminating reactor')
        for w in self._workers.values():
            w.delete(True)
        self._socket.close()
        self._socket = None

    def stop(self):
        self._shutting_down = True

    def destroy(self):
        if self._socket:
            self._socket.close()
            self._socket = None

    @property
    def socket(self):
        return self._socket

    def forget_worker(self, worker_addr):
        self._workers.pop(worker_addr)

    def _make_socket(self, socktype):
        socket = self._context.socket(socktype)
        socket.linger = 0
        return socket

    def _handle_message(self, rmsg):
        sender_addr = rmsg.pop()
        assert rmsg.pop() == ''
        magic = rmsg.pop()
        if magic == MDP.C_CLIENT:
            self._handle_client(sender_addr, rmsg)
        elif magic == MDP.W_WORKER:
            self._handle_worker(sender_addr, rmsg)
        else:
            raise err.UnknownMagic(magic)

    def _handle_client(self, sender_addr, rmsg):
        service_name = rmsg.pop()
        service = self._require_service(service_name)
        service.queue_request(sender_addr, rmsg, self._request_timeout)
        service.dispatch()

    def _handle_worker(self, sender_addr, rmsg):
        worker = self._require_worker(sender_addr)
        command = rmsg.pop()
        self.heartbeat.hear_from(sender_addr)
        if command == MDP.W_READY:
            service_name = rmsg.pop()
            service = self._require_service(service_name)
            worker.register(service)
            worker.ready()
        elif command == MDP.W_REPLY:
            client_addr = rmsg.pop()
            worker.handle_reply(client_addr, rmsg)
            worker.ready()
        elif command == MDP.W_HEARTBEAT:
            log_heartbeat.debug('recv heartbeat %s', worker)
            return
        else:
            log.error('Unknown command from %s: %s', hexlify(sender_addr), command)
            raise NotImplementedError()

    def _require_service(self, service_name):
        service = self._services.get(service_name)
        if service is None:
            service = _Service(self, service_name)
            self._services[service_name] = service
        return service

    def _require_worker(self, worker_addr):
        worker = self._workers.get(worker_addr)
        if worker is None:
            worker = _Worker(self, worker_addr)
            self._workers[worker_addr] = worker
        return worker

    def _send_heartbeats(self):
        for addr in self.heartbeat.need_beats():
            worker = self._require_worker(addr)
            worker.send(MDP.W_HEARTBEAT)

    def _reap_workers(self):
        for addr in self.heartbeat.reap():
            worker = self._require_worker(addr)
            worker.delete(False)


class SecureMajorDomoBroker(zutil.SecureServer, MajorDomoBroker):

    def __init__(self, key, *args, **kwargs):
        zutil.SecureServer.__init__(self, key)
        MajorDomoBroker.__init__(self, *args, **kwargs)


class _Worker(object):

    def __init__(self, broker, addr):
        self._broker = broker
        self._addr = addr
        self._service = None

    @property
    def addr(self):
        return self._addr

    def __repr__(self):
        return '<Worker {}: {}>'.format(hexlify(self._addr), self._service)

    def register(self, service):
        if self._service:
            log.debug('Worker already registered for %s', self._service)
            self.delete(True)
        else:
            self._service = service

    def ready(self):
        self._service.worker_ready(self)
        self._service.dispatch()

    def send(self, command, *parts):
        prefix = [self._addr, '', MDP.W_WORKER, command]
        self._broker.socket.send_multipart(prefix + list(parts))
        self._broker.heartbeat.send_to(self._addr)

    def delete(self, disconnect):
        log.info('Disconnecting worker %s', hexlify(self._addr))
        if disconnect:
            self.send(MDP.W_DISCONNECT)
        if self._service is not None:
            self._service.unregister_worker(self)
        self._broker.forget_worker(self._addr)

    def handle_request(self, client_addr, rmsg):
        '''Handle a request from a client by sending to the worker'''
        payload = list(reversed(rmsg))
        self.send(MDP.W_REQUEST, client_addr, '', *payload)

    def handle_reply(self, client_addr, rmsg):
        '''Handle a reply from a worker by sending to the client'''
        assert rmsg.pop() == ''
        if self._service:
            self._service.send_to_client(client_addr, list(reversed(rmsg)))
        else:
            self.delete(True)


class _Service(object):

    def __init__(self, broker, name):
        self._broker = broker
        self._name = name
        self._requests = deque()        # (exp, sender, body)
        self._workers_ready = deque()   # workers possibly available
        self._workers = {}              # all registered workers

    def __repr__(self):
        return '<Service {}: {}q, {}r, {}w>'.format(
            self._name,
            len(self._requests),
            len(self._workers_ready),
            len(self._workers))

    @property
    def name(self):
        return self._name

    def send_to_client(self, client_addr, payload):
        prefix = [client_addr, '', MDP.C_CLIENT, self._name]
        self._broker.socket.send_multipart(prefix + payload)

    def worker_ready(self, worker):
        log.debug('%s: ready worker %s', self.name, worker)
        self._workers_ready.appendleft(worker.addr)
        self._workers[worker.addr] = worker

    def unregister_worker(self, worker):
        log.info('%s: unregister %s', self.name, worker)
        self._workers.pop(worker.addr, None)

    def queue_request(self, client_addr, rmsg, timeout):
        log.debug('queueing request from %s on %s', hexlify(client_addr), self.name)
        log.debug('workers ready:')
        for addr in self._workers_ready:
            log.debug(' - %s', hexlify(addr))
        self._requests.appendleft((time.time() + timeout, client_addr, rmsg))

    def dispatch(self):
        while self._requests and self._workers_ready:
            (exp, client_addr, rmsg) = self._requests.pop()
            if exp < time.time():       # Skip expired requests
                continue
            worker = self.pop_ready_worker()
            if worker is not None:
                worker.handle_request(client_addr, rmsg)
                break
            self._requests.append((exp, client_addr, rmsg))

    def pop_ready_worker(self):
        while self._workers_ready:
            addr = self._workers_ready.pop()
            worker = self._workers.get(addr)
            if worker is not None:
                return worker
        return None

if __name__ == '__main__':
    main()


