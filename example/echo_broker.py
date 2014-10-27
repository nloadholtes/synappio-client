import sys
import logging.config

from seas.zutil.mdp import MajorDomoBroker

logging.config.fileConfig('logging.ini')


def main():
    broker = MajorDomoBroker(sys.argv[1])
    broker.serve_forever()

if __name__ == '__main__':
    main()
