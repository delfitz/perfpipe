import logging
import argparse
import os
from functools import partial

from utils.logger import logConfig
from utils.asyncUtils import asyncRunner

import stats.clock as clock
import stats.weather as weather
import stats.mpstats as mpstats
import stats.cpuprocs as cpuprocs
import stats.vnstats as vnstats


def testProxy(args):
    pass


def clockProxy(args):
    asyncRunner(clock.runner, args.pipe)
    logging.info('exited clock')


def weatherProxy(args):
    if not args.key:
        apiKey = os.getenv('WEATHER')
        if not apiKey:
            logging.info('no api key found')
            return
    else:
        apiKey = args.key
    logging.info(f'apikey: {apiKey}')
    asyncRunner(weather.runner, args.pipe, args.location, apiKey)
    logging.info('exited weather')


def cpuprocsProxy(args):
    asyncRunner(cpuprocs.runner, args.pipe)
    logging.info('exited cpuprocs')


def mpstatsProxy(args):
    asyncRunner(mpstats.runner, args.pipe)
    logging.info('exited mpstats')


def vnstatsProxy(args):
    asyncRunner(partial(vnstats.runner, args.pipe))
    logging.info('exited vnstats')


def addSubparser(subparsers, name, proxy):
    sub = subparsers.add_parser(name)
    sub.add_argument('--pipe', default=None)
    sub.set_defaults(func=proxy)
    return sub


def parseArgs():
    parser = argparse.ArgumentParser(prog='command')
    subparsers = parser.add_subparsers()

    addSubparser(subparsers, 'clock', clockProxy)

    weather_parser = addSubparser(subparsers, 'weather', weatherProxy)
    weather_parser.add_argument('--location', default=None)
    weather_parser.add_argument('--key', default=None)

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
