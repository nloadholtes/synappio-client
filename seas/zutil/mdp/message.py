from . import err

class MDP:
    W_READY = '\x01'
    W_REQUEST = '\x02'
    W_REPLY = '\x03'
    W_HEARTBEAT = '\x04'
    W_DISCONNECT = '\x05'
    W_WORKER = 'MDPW01'
    C_CLIENT = 'MDPC01'


class Message(object):

    def __init__(self, message):
        self.message = message

    @classmethod
    def parse(cls, msg):
        try:
            empty, proto = msg[:2]
            if empty != '':
                raise err.InvalidMessage('First frame must be empty', msg)
            if proto == MDP.C_CLIENT:
                return ClientMessage(msg)
            elif proto == MDP.W_WORKER:
                return WorkerMessage.parse(msg)
            else:
                raise err.InvalidMessage('Unknown protocol {}'.format(proto), msg)


class ClientMessage(Message):

    @classmethod
    def new(cls, *body):

    pass


class WorkerMessage(Message):
    pass


class WorkerReady(WorkerMessage):
    pass


class WorkerRequest(WorkerMessage):
    pass


class WorkerReploy(WorkerMessage):
    pass


class WorkerHeartbeat(WorkerMessage):
    pass


class WorkerDisconnect(WorkerMessage):
    pass

