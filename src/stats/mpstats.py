import logging
import json
import asyncio

# from utils.asyncUtils import createTask
from utils.pipeUtils import processRunner, pipeWriter
from utils.formatting import highlightStat, getSparkline, getIcon

STATS_CMD = 'mpstat -P ALL 1'
STATS_COLS = [0, 10]
STATS_PIPE = '/tmp/mpstats-pipe'

SENSORS_CMD = 'sensors -j'
TEMP_PATH = ('k10temp-pci-00c3', 'Tctl', 'temp1_input')
FAN_PATH = ('system76_io-virtual-0', 'CPUF', 'fan1_input')

TEMP_SPLITS = [20, 30, 50, 70, 90]
FAN_SPLITS = [0, 1000, 2000, 2500, 3000]


async def getSensors():
    proc = await asyncio.create_subprocess_shell(
        SENSORS_CMD,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL)
    stdout, _ = await proc.communicate()
    data = json.loads(stdout.decode('utf-8'))
    cpuTemp = data[TEMP_PATH[0]][TEMP_PATH[1]][TEMP_PATH[2]]
    cpuFan = data[FAN_PATH[0]][FAN_PATH[1]][FAN_PATH[2]]
    return cpuTemp, cpuFan


async def lineFormatter(data):
    cpus = [100. - float(usage) for _, usage in data[1:]]
    cpuTemp, cpuFan = await getSensors()
    tempLabel = f'{getIcon("", False)}{highlightStat(cpuTemp, TEMP_SPLITS, unit="°C")}'
    fanLabel = f'{getIcon("", False)}{highlightStat(cpuFan, FAN_SPLITS, unit="rpm", decimals=0)}'
    allCpuLabel = highlightStat(cpus[0])
    mpSparkline = getSparkline(cpus[1:])
    cpuIcon = getIcon('')
    barline = f'  {cpuIcon} {allCpuLabel} {tempLabel} {fanLabel} {mpSparkline}'
    return barline


async def runner(pipe):
    try:
        await processRunner(pipe, STATS_CMD, STATS_COLS, lineFormatter)
    except asyncio.CancelledError:
        logging.info('caught runner cancellation')
        await pipeWriter(pipe, 'mpstats monitor exited')
