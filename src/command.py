import logging
import argparse
from functools import partial

from utils.logger import logConfig
from utils.asyncUtils import asyncRunner

import stats.vnstats as vnstats
# import stats.asyncPipe as asyncPipe


def testProxy(args):
    pass


def vnstatsProxy(args):
    asyncRunner(partial(vnstats.run, args.pipe))
    logging.info('exited vnstats')


def parseArgs():
    parser = argparse.ArgumentParser(prog='command')
    subparsers = parser.add_subparsers()

    vnstats_parser = subparsers.add_parser('vnstats')
    vnstats_parser.add_argument('--pipe', default=True)
    vnstats_parser.set_defaults(func=vnstatsProxy)

    test_parser = subparsers.add_parser('test')
    test_parser.add_argument('--pipe', default=True)
    test_parser.set_defaults(func=testProxy)

    args = parser.parse_args()
    if 'func' in vars(args):
        return args
    else:
        parser.print_help()


def setup():
    logConfig()
    args = parseArgs()
    args.func(args)


if __name__ == '__main__':
    setup()
