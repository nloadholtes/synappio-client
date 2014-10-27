import sys
import logging.config

from seas.zutil.auth import Key
from seas.zutil.mdp import SecureMajorDomoWorker

logging.config.fileConfig('logging.ini')


def main():
    client_key = Key.load('example/worker.key_secret')
    server_key = Key.load('example/broker.key')
    broker = SecureMajorDomoWorker(
        server_key, client_key, sys.argv[1], 'echo', echo)
    broker.serve_forever()

def echo(*args):
    return args

if __name__ == '__main__':
    main()
