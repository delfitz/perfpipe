import logging
import argparse
from functools import partial

from utils.logger import logConfig
from utils.asyncUtils import asyncRunner

import stats.mpstats as mpstats
import stats.cpuprocs as cpuprocs
import stats.vnstats as vnstats


def testProxy(args):
    pass


def cpuprocsProxy(args):
    asyncRunner(cpuprocs.runner, args.pipe)
    logging.info('exited cpuprocs')


def mpstatsProxy(args):
    asyncRunner(mpstats.runner, args.pipe)
    logging.info('exited mpstats')


def vnstatsProxy(args):
    asyncRunner(partial(vnstats.runner, args.pipe))
    logging.info('exited vnstats')


def parseArgs():
    parser = argparse.ArgumentParser(prog='command')
    subparsers = parser.add_subparsers()

    vnstats_parser = subparsers.add_parser('vnstats')
    vnstats_parser.add_argument('--pipe', default=True)
    vnstats_parser.set_defaults(func=vnstatsProxy)

    cpuprocs_parser = subparsers.add_parser('cpuprocs')
    cpuprocs_parser.add_argument('--pipe', default=True)
    cpuprocs_parser.set_defaults(func=cpuprocsProxy)

    mpstats_parser = subparsers.add_parser('mpstats')
    mpstats_parser.add_argument('--pipe', default=True)
    mpstats_parser.set_defaults(func=mpstatsProxy)

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
