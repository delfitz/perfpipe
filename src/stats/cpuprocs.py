import logging
import json
import asyncio

# from utils.asyncUtils import createTask
from utils.pipeUtils import processRunner, pipeWriter
from utils.formatting import highlightStat, getBox

STATS_CMD = 'pidstat -u 2'
STATS_COLS = [8, 6]
STATS_PIPE = '/tmp/cpuprocs-pipe'


async def lineFormatter(data):
    procs = [(name, float(usage)) for name, usage in data[1:]]
    if procs:
        procs.sort(key=lambda x: x[1], reverse=True)

    procLine = ''
    for proc in procs[:3]:
        procLabel = f'{highlightStat(proc[1], label=proc[0])}'
        procLine += getBox(procLabel)
    return procLine


async def runner(pipe):
    try:
        await processRunner(pipe, STATS_CMD, STATS_COLS, lineFormatter)
    except asyncio.CancelledError:
        logging.info('caught runner cancellation')
        await pipeWriter(pipe, 'cpuprocs monitor exited')
