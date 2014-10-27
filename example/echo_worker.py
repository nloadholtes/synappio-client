import sys
import logging.config

from seas.zutil.mdp import MajorDomoWorker

logging.config.fileConfig('logging.ini')


def main():
    broker = MajorDomoWorker(sys.argv[1], 'echo', echo)
    broker.serve_forever()

def echo(*args):
    return args

if __name__ == '__main__':
    main()
