import zmq.auth

class Key(object):

    def __init__(self, public, secret=None):
        self.public = public
        self.secret = secret

    @classmethod
    def generate(cls):
        public, secret = zmq.curve_keypair()
        return cls(public, secret)

    @classmethod
    def load(cls, filename):
        public, secret = zmq.auth.load_certificate(filename)
        return cls(public, secret)

    def apply(self, socket):
        socket.curve_publickey = self.public
        socket.curve_secretkey = self.secret


