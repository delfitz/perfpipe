import logging
import asyncio

from datetime import datetime

from utils.formatting import formatClock
from utils.pipeUtils import pipeWriter

SPARK_LEN = 8
HL_SPLITS = [-100, -100, 29, 31, 35]


def getClockIcon(dt):
    clocks = [
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
    ]
    return clocks[dt.hour % 12]


def getClock():
    dt = datetime.now()
    line = formatClock(dt, getClockIcon(dt))
    return line


async def runner(pipe, **kwargs):
    try:
        while True:
            logging.info(f'updating clock: {pipe}')
            update = getClock()
            await pipeWriter(pipe, update)
            await asyncio.sleep(61 - datetime.now().second)
    except asyncio.CancelledError:
        logging.info('caught runner cancellation')
        await pipeWriter(pipe, 'clock exited')
