import logging
import json
import asyncio
from functools import partial

from utils.pipeUtils import processRunner, processCommand, pipeWriter
from utils.formatting import formatStat, formatLabel, getIcon, ICON_LARGE
from utils.sparkUtils import getSparkline

HOST_CMD = 'hostnamectl'
HOST_NAME = 'Static hostname'
HOST_KERNEL = 'Kernel'

MEM_CMD = 'cat /proc/meminfo'
MEM_TOTAL = 'MemTotal'
MEM_AVAIL = 'MemAvailable'

STATS_CMD = 'mpstat -P ALL 1'
STATS_COLS = [0, 10]
STATS_PIPE = '/tmp/mpstats-pipe'

SENSORS_CMD = 'sensors -j'
TEMP_PATH = ('k10temp-pci-00c3', 'Tctl', 'temp1_input')
FAN_PATH = ('system76_io-virtual-0', 'CPUF', 'fan1_input')

TEMP_SPLITS = [20, 30, 50, 70, 90]
FAN_SPLITS = [0, 1000, 2000, 2500, 3000]

HOST_ICON = ''
CPU_ICON = ''
MEM_ICON = ''
SEN_ICON = ''


async def getHostInfo():
    result, _ = await processCommand(HOST_CMD)
    lines = [
        line.lstrip() for line in result.decode('utf-8').split('\n') if line
    ]
    logging.info(lines)
    info = {line.split(':')[0]: line.split(':')[1].lstrip() for line in lines}
    host = f'{formatLabel(info[HOST_NAME])}'
    kernel = f' {formatLabel(info[HOST_KERNEL].split()[1], sub=True)}'
    return f'{host}{kernel}'


async def getMemInfo():
    result, _ = await processCommand(MEM_CMD)
    lines = [line for line in result.decode('utf-8').split('\n') if line]
    info = {line.split()[0][:-1]: float(line.split()[1]) for line in lines}
    memUsed = (1 - (info[MEM_AVAIL] / info[MEM_TOTAL])) * 1e2
    memFree = info[MEM_AVAIL] * 1e-6
    return f'{formatStat(memUsed, icon=MEM_ICON)} {formatStat(memFree, unit="GB")}'


async def getSensors():
    result, _ = await processCommand(SENSORS_CMD)
    data = json.loads(result.decode('utf-8'))
    cpuTemp = data[TEMP_PATH[0]][TEMP_PATH[1]][TEMP_PATH[2]]
    cpuFan = data[FAN_PATH[0]][FAN_PATH[1]][FAN_PATH[2]]
    tempLabel = formatStat(cpuTemp, unit="°C", icon=SEN_ICON)
    fanLabel = formatStat(cpuFan, unit="rpm", decimals=0)
    return f'{tempLabel} {fanLabel}'


async def lineFormatter(hostInfo, data):
    cpus = [100. - float(usage) for _, usage in data[1:]]
    hostIcon = getIcon(HOST_ICON, size=ICON_LARGE)
    allCpuLabel = formatStat(cpus[0], icon=CPU_ICON)
    memLabel = await getMemInfo()
    sensorLabel = await getSensors()
    stats = f'{hostIcon}   {hostInfo}  {allCpuLabel}  {memLabel}  {sensorLabel}'
    mpSparkline = getSparkline(cpus[1:])
    return f'{stats} {mpSparkline}'


async def runner(pipe):
    try:
        hostInfo = await getHostInfo()
        logging.info(hostInfo)
        await processRunner(pipe, STATS_CMD, STATS_COLS,
                            partial(lineFormatter, hostInfo))
    except asyncio.CancelledError:
        logging.info('caught runner cancellation')
        await pipeWriter(pipe, 'mpstats monitor exited')
