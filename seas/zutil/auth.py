import zmq

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


class SecureProxy(threading.Thread):
    '''Acts as a client to an insecure LB, worker to a secure LB'''

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


