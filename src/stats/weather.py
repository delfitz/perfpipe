import logging
import aiohttp
import asyncio

from datetime import datetime
from utils.formatting import formatWeather, formatLabel

from utils.pipeUtils import pipeWriter
from utils.linkUtils import getLinkInfo

SPARK_LEN = 8
HL_SPLITS = [-100, -100, 29, 31, 35]

URL = 'https://api.openweathermap.org/data/3.0/onecall'
LOC = 'name'
DESC = 'location'
LAT = 'lat'
LON = 'lon'
LOCS = [
    {
        LOC: 'nyc',
        DESC: 'NYC',
        LAT: 40.72,
        LON: -74.00
    },
    {
        LOC: 'sag',
        DESC: 'Sag Harbor',
        LAT: 41.00,
        LON: -72.29
    },
]
EXCLUDE = 'exclude'
UNITS = 'units'
APPID = 'appid'

EXCLUDES = 'daily,alerts'
METRIC = 'metric'
HOME = 'nyc'


def getLocation(location):
    locs = {data[LOC]: data for data in LOCS}
    if location:
        if location in locs:
            return locs[location]
    else:
        return locs[HOME]


def getPayload(loc, apiKey):
    return {
        LAT: loc[LAT],
        LON: loc[LON],
        EXCLUDE: EXCLUDES,
        UNITS: METRIC,
        APPID: apiKey
    }


def getWeatherIcon(icon):
    icons = {
        'sunny': ' ',
        'night': '望',
        'partlyCloudy': ' ',
        'cloudyNight': ' ',
        'cloudy': ' ',
        'rain': ' ',
        'thunderstorm': ' ',
        'snow': ' ',
        'unknown': ' '
    }

    if icon == '01d':
        return icons['sunny']
    elif icon == '01n':
        return icons['night']
    elif icon in ('02d', '03d'):
        return icons['partlyCloudy']
    elif icon in ('02n', '03n', '04n'):
        return icons['cloudyNight']
    elif icon == '04d':
        return icons['cloudy']
    elif icon in ('09d', '10d', '09n', '10n'):
        return icons['rain']
    elif icon == '11d':
        return icons['thunderstorm']
    elif icon == '13d':
        return icons['snow']
    else:
        return icons['unknown']


def weatherFormatter(temp, icon, date=None):
    temp = f'{temp:.0f}'
    date = f'{date:%-I%p}' if date else ''
    return f'{temp}{icon}{date}'


def parseForecast(data, minutely=False):
    return {
        'date': datetime.fromtimestamp(data['dt']),
        'temp': data['temp'],
        'clouds': data['clouds'],
        'icon': getWeatherIcon(data['weather'][0]['icon']),
        'cond': data['weather'][0]['description']
    }


def getCurrent(data):
    current = parseForecast(data['current'])
    return formatWeather(current['temp'],
                         icon=current['icon'],
                         hl_splits=HL_SPLITS)


def getHourly(data, hours=24):
    forecasts = [parseForecast(hourly) for hourly in data['hourly'][:hours]]
    return [
        weatherFormatter(hourly['temp'], hourly['icon'], hourly['date'])
        for hourly in forecasts
    ]


def getHourlyCollapsed(data, numDeltas=4):
    forecasts = [parseForecast(hourly) for hourly in data['hourly']]
    deltas = []
    initial = forecasts[0]
    for hourly in forecasts[1:]:
        test = deltas[-1] if deltas else initial
        if hourly['icon'] != test['icon']:
            deltas.append(hourly)
        elif abs(hourly['temp'] - test['temp']) > 1.9:
            deltas.append(hourly)
    return [
        formatWeather(delta['temp'],
                      icon=delta['icon'],
                      date=delta['date'],
                      hl_splits=HL_SPLITS) for delta in deltas
    ]


async def getWeather(session, loc, payload):
    try:
        async with session.get(URL, params=payload) as resp:
            forecasts = await resp.json()
            current = getCurrent(forecasts)
            hourly = getHourly(forecasts)
            collapsed = getHourlyCollapsed(forecasts)
            logging.debug(f'hourly: {" ".join(hourly[1:])}')
            return f'{formatLabel(loc[DESC], False)} {current}  {" ".join(collapsed[:5])}'
    except aiohttp.ClientConnectionError:
        logging.info('connection error')
        return None
    except Exception as e:
        logging.info(f'uncaught: {e}')
        return None


async def runner(pipe, location, apiKey):
    loc = getLocation(location)
    payload = getPayload(loc, apiKey)
    try:
        while True:
            _, error = await getLinkInfo()
            if error:
                await pipeWriter(pipe, error)
            else:
                async with aiohttp.ClientSession(conn_timeout=1) as session:
                    while True:
                        if weather := await getWeather(session, loc, payload):
                            await pipeWriter(pipe, weather)
                            await asyncio.sleep(600)
                        else:
                            break
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logging.info('caught runner cancellation')
        await pipeWriter(pipe, 'weather monitor exited')
