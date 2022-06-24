import logging
import asyncio

from utils.pipeUtils import processRunner, pipeWriter
from utils.formatting import formatStat

STATS_CMD = 'pidstat -u 2'
STATS_COLS = [8, 6]
STATS_PIPE = '/tmp/cpuprocs-pipe'

PROC_ICON = ''


async def lineFormatter(data):
    procs = [(name, float(usage)) for name, usage in data[1:]]
    if procs:
        procs.sort(key=lambda x: x[1], reverse=True)

    procLine = ''
    for proc in procs[:3]:
        procLabel = f'{formatStat(proc[1], label=proc[0], icon=PROC_ICON)}  '
        procLine += procLabel
    return procLine


async def runner(pipe, **kwargs):
    try:
        await processRunner(pipe, STATS_CMD, STATS_COLS, lineFormatter)
    except asyncio.CancelledError:
        logging.info('caught runner cancellation')
        await pipeWriter(pipe, 'cpuprocs monitor exited')
