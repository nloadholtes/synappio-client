import time
import logging
from collections import deque


log = logging.getLogger(__name__)


class HeartbeatManager(object):

    def __init__(self, interval, liveness):
        self.interval = interval
        self.liveness = liveness
        self.heard_from = deque()
        self.sent_to = deque()
        self.peers = {}

    def require_peer(self, addr):
        peer = self.peers.get(addr, None)
        if peer is None:
            peer = self.peers[addr] = Peer(addr)
            self.heard_from.appendleft((time.time(), addr))
            self.sent_to.appendleft((time.time(), addr))
        return peer

    def discard_peer(self, addr):
        self.peers.pop(addr, None)

    def hear_from(self, addr):
        self.heard_from.appendleft((time.time(), addr))
        peer = self.require_peer(addr)
        peer.hear_from()

    def send_to(self, addr):
        self.sent_to.appendleft((time.time(), addr))
        peer = self.require_peer(addr)
        peer.send_to()

    def need_beats(self):
        '''Anyone who hasn't been sent to since `now - interval` needs a heartbeat'''
        beat_threshold = time.time() - self.interval
        while self.sent_to and self.sent_to[-1][0] < beat_threshold:
            _, addr = self.sent_to.pop()
            peer = self.peers.get(addr)
            if peer is None:
                continue    # peer was discarded
            if peer.last_sent_to < beat_threshold:
                yield peer.addr

    def reap(self):
        '''Anyone who we haven't heard from since (now - interval * liveness)
        is dead.
        '''
        expiration = time.time() - (self.interval * self.liveness)
        while self.heard_from and self.heard_from[-1][0] < expiration:
            _, addr = self.heard_from.pop()
            peer = self.peers.get(addr)
            if peer is None:
                continue    # peer was discarded
            if peer.last_heard_from < expiration:
                self.discard_peer(addr)
                yield addr


class Peer(object):

    def __init__(self, addr):
        self.addr = addr
        self.last_heard_from = time.time()
        self.last_sent_to = time.time()

    def hear_from(self):
        self.last_heard_from = max(time.time(), self.last_heard_from)

    def send_to(self):
        self.last_sent_to = max(time.time(), self.last_heard_from)

