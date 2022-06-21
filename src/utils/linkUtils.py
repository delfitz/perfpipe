from utils.pipeUtils import processCommand
from utils.formatting import formatStat, formatLabel

LINK_INFO = 'iw dev wlan0 link'
LINK_SSID = 'SSID'
LINK_FREQ = 'freq'
LINK_SIGNAL = 'signal'
LINK_SPLITS = [-40, -65, -80, -90, -95]


async def getLinkInfo():
    stdout, stderr = await processCommand(LINK_INFO)
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

    ssid = formatLabel(status[LINK_SSID])
    level, unit = status[LINK_SIGNAL].split()
    signal = formatStat(int(level),
                        unit=unit,
                        decimals=0,
                        highlight=True,
                        hl_splits=LINK_SPLITS)
    return f'{signal} {ssid}'
