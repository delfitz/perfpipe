import logging
import json
import asyncio
from functools import partial

from utils.asyncUtils import createTask
from utils.pipeUtils import pipeWriter
from utils.linkUtils import getLinkInfo, linkFormatter
from utils.formatting import formatStat, getIcon
from utils.sparkUtils import getSparkline

STATS_CMD = 'vnstat --live --json'
STATS_PIPE = '/tmp/vnstats-pipe'

LINK_INFO = 'iw dev wlan0 link'
LINK_SSID = 'SSID'
LINK_FREQ = 'freq'
LINK_SIGNAL = 'signal'
LINK_SPLITS = [-40, -65, -80, -90, -95]

TX = 'tx'
RX = 'rx'
RATE = 'bytespersecond'
HL_SPLITS = [0, 2**10, 2**20, 2**23, 2**25]
SPARK_SPLITS = [0.0, 2**10, 2**15, 2**18, 2**20, 2**22, 2**23, 2**24]
SPARK_LEN = 8

RX_ICON = ''
TX_ICON = ''


def rateFormatter(rate, icon):
    unit = 'kB/s' if rate < 1e6 else 'GB/s'
    return formatStat(rate * 1e-3,
                      unit=unit,
                      highlight=True,
                      hl_splits=HL_SPLITS,
                      icon=icon)


def lineFormatter(dataBuffer, linkInfo):
    rates = [(data[RX][RATE], data[TX][RATE]) for data in dataBuffer]
    rxLabel = rateFormatter(rates[-1][0], RX_ICON)
    txLabel = rateFormatter(rates[-1][1], TX_ICON)
    rxSparkline = getSparkline([rx for rx, _ in rates], HL_SPLITS, SPARK_SPLITS)
    return f'{rxSparkline} {rxLabel} {txLabel}  {linkInfo}  '


async def processMonitor(stdout, writer):
    _ = await stdout.readline()
    dataBuffer = []
    async for line in stdout:
        if b'Error' in line:
            logging.info(f'vnstat exited: {line}')
            return

        info, error = await getLinkInfo()
        if error:
            logging.info(f'link error: {error}')
            return

        data = line.decode('utf-8').rstrip('\n')
        dataBuffer.append(json.loads(data))
        dataBuffer = dataBuffer[-SPARK_LEN:]
        logging.debug(f'{dataBuffer[-1]}')
        await writer(lineFormatter(dataBuffer, linkFormatter(info)))


async def runner(pipe):
    try:
        while True:
            info, error = await getLinkInfo()
            if error:
                await pipeWriter(pipe, error)
            else:
                proc = await asyncio.create_subprocess_shell(
                    STATS_CMD,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                )
                monitorTask = createTask(
                    processMonitor(proc.stdout, partial(pipeWriter, pipe)),
                    'monitor')
                await monitorTask
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logging.info('caught runner cancellation')
        await pipeWriter(pipe, 'vnstats monitor exited')
