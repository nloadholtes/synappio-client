import sys
import logging.config

from seas.zutil.mdp import MajorDomoProxy

logging.config.fileConfig('logging.ini')


def main():
    proxy = MajorDomoProxy(
        uri_upstream=sys.argv[1],
        uri_downstream=sys.argv[2],
        service='echo')
    proxy.serve_forever()

if __name__ == '__main__':
    main()
