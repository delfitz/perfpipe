import logging
import json
import asyncio
from functools import partial

from utils.asyncUtils import createTask
from utils.formatting import getSparkline, highlightStat, highlightLabel, getIcon

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


async def pipeWriter(pipe, data):
    with open(pipe, 'wt') as p:
        p.write(f'{data}\n')


async def getLinkInfo():
    proc = await asyncio.create_subprocess_shell(LINK_INFO,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if stderr:
        return None, 'no wifi link'
    elif b'Not connected' in stdout:
        return None, 'no connection'
    else:
        return stdout, None


def linkFormatter(info):
    status = {}
    lines = info.decode('utf-8').split('\n')
    for line in lines[1:]:
        if line:
            param, value = [x.strip() for x in line.split(':')]
            if param == LINK_SSID:
                status[LINK_SSID] = value
            elif param == LINK_FREQ:
                status[LINK_FREQ] = value
            elif param == LINK_SIGNAL:
                status[LINK_SIGNAL] = value

    ssid = highlightLabel(status[LINK_SSID])
    level, unit = status[LINK_SIGNAL].split()
    signal = highlightStat(int(level), LINK_SPLITS, unit=unit, decimals=0)
    return f'{signal} {ssid}'


def rateFormatter(rate):
    if rate < 1e6:
        rateFormat = highlightStat(rate * 1e-3, HL_SPLITS, unit='kB/s')
    else:
        rateFormat = highlightStat(rate * 1e-6, HL_SPLITS, unit='MB/s')
    return rateFormat


def lineFormatter(dataBuffer, linkInfo):
    rates = [(data[RX][RATE], data[TX][RATE]) for data in dataBuffer]
    rxSparkline = getSparkline([rx for rx, _ in rates], HL_SPLITS, SPARK_SPLITS)
    rxLabel = f'{getIcon("", False)}{rateFormatter(rates[-1][0])}'
    txLabel = f'{getIcon("", False)}{rateFormatter(rates[-1][1])}'
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
