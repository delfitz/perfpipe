import logging
import argparse
import os
import asyncio

from utils.logger import logConfig
from utils.asyncUtils import asyncRunner, createTask

import stats.clock as clock
import stats.weather as weather
import stats.mpstats as mpstats
import stats.cpuprocs as cpuprocs
import stats.vnstats as vnstats

PERF_PATH = '/tmp/perfpipe/'
PERF_LOG = 'perfpipe.log'

MODS = {
    'clock': clock.runner,
    'weather': weather.runner,
    'vnstats': vnstats.runner,
    'mpstats': mpstats.runner,
    'cpuprocs': cpuprocs.runner,
}


def getPipe(mod):
    pipe = f'{PERF_PATH}{mod}-pipe'
    if not os.path.exists(pipe):
        os.mkfifo(pipe)
    return pipe


async def proxyRunner(args):
    if not os.path.exists(PERF_PATH):
        os.mkdir(PERF_PATH)
    optionals = {k: v for k, v in vars(args).items() if v is not None}
    if args.mod and args.mod in MODS:
        logConfig()
        logging.info(f'starting module {args.mod}')
        await MODS[args.mod](getPipe(args.mod), **optionals)
        logging.info(f'module {args.mod} finished')
    else:
        logConfig(file=f'{PERF_PATH}{PERF_LOG}')
        tasks = [
            createTask(MODS[mod](getPipe(mod), **optionals), mod)
            for mod in MODS
        ]
        await asyncio.gather(*tasks)
        logging.info('all mods exited')


def parseArgs():
    parser = argparse.ArgumentParser(prog='command')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--mod', choices=MODS.keys())
    parser.add_argument('--key')
    parser.add_argument('--loc')

    args = parser.parse_args()
    if vars(args)['mod'] or vars(args)['all']:
        asyncRunner(proxyRunner, args)
    else:
        parser.print_help()


if __name__ == '__main__':
    parseArgs()
