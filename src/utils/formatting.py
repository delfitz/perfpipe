import logging
import utils.base16Colors as bfc

HL_LABEL = bfc.BASE0D
HL_ICON = bfc.BASE0C

HL_INACTIVE = bfc.BASE01
HL_LOW = bfc.BASE03
HL_MODERATE = bfc.BASE0D
HL_ACTIVE = bfc.BASE0A
HL_HIGH = bfc.BASE09
HL_CRITICAL = bfc.BASE08

HL_INFO = bfc.BASE01
HL_NORMAL = bfc.BASE03
HL_WARN = bfc.BASE09

HL_COLORS = [HL_INACTIVE, HL_LOW, HL_MODERATE, HL_ACTIVE, HL_HIGH, HL_CRITICAL]
HL_SPLITS = [0.1, 3, 10, 50, 90]

SPARK_CHARS = u'▁▁▂▃▄▅▆▇█'
SPARK_SPLITS = [0.0, 1, 2, 3, 5, 10, 50, 90]


def bucket(value, splits):
    for idx, split in enumerate(splits):
        if splits[0] > splits[-1]:
            if value >= split:
                return idx
        else:
            if value <= split:
                return idx
    return len(splits)


def getColor(base, theme=bfc.PALENIGHT):
    return bfc.getTheme(theme)[base]


def getHighlight(level, splits, theme=bfc.PALENIGHT):
    return getColor(HL_COLORS[bucket(level, splits)])


def getSparkChar(level, splits):
    return SPARK_CHARS[bucket(level, splits)]


def getSparkFormat(level,
                   hl_splits=HL_SPLITS,
                   spark_splits=SPARK_SPLITS,
                   theme=bfc.PALENIGHT):
    highlight = getHighlight(level, hl_splits)
    spark = getSparkChar(level, spark_splits)
    return highlight, spark


def getSparkline(levels, hl_splits=HL_SPLITS, spark_splits=SPARK_SPLITS):
    sparkline = ''
    for level in levels:
        color, spark = getSparkFormat(level, hl_splits, spark_splits)
        sparkline += f'<fc={color}>{spark}</fc>'
    return f'<fn=1>{sparkline}</fn>'


def formatClock(dt, icon):
    timeLabel = f'{dt:%-I:%M}<fn=1>{dt:%p}</fn>'
    iconLabel = f' <fn=8><fc={getColor(HL_ICON)}>{icon}</fc></fn>  '
    dateLabel = f'{dt:%A, %B %-d}'
    clockLabel = f'{timeLabel} {iconLabel} {dateLabel}'
    # formatted = f'g9qQ hijk'
    formatted = f'<fn=2><fc={getColor(HL_LABEL)}>{clockLabel}</fc></fn>'
    logging.info(formatted)
    return formatted


def highlightWeather(temp,
                     icon=None,
                     date=None,
                     unit=None,
                     hl_splits=HL_SPLITS,
                     theme=bfc.PALENIGHT):
    tempFont = 2 if date else 3
    iconFont = 6 if date else 7

    hourLabel = f'<fn=1><fc={getColor(HL_LABEL)}>{date:%-I%p}</fc></fn>' if date else ''
    tempUnit = f'{temp:.0f}'
    tempLabel = f'<fn={tempFont}><fc={getHighlight(temp, hl_splits)}>{tempUnit}</fc></fn>'
    iconLabel = f'<fn={iconFont}><fc={getColor(HL_ICON)}>{icon}</fc></fn>'
    return f'{tempLabel}{iconLabel}{hourLabel}'


def highlightStat(level,
                  hl_splits=HL_SPLITS,
                  label=None,
                  unit='%',
                  decimals=1,
                  theme=bfc.PALENIGHT):
    statLabel = f'{label} ' if label else ''
    statLine = f'{statLabel}{level:.{decimals}f}<fn=1>{unit}</fn>'
    return f'<fc={getHighlight(level, hl_splits)}>{statLine}</fc>'


def highlightLabel(label, highlight=HL_NORMAL, theme=bfc.PALENIGHT):
    return f'<fc={getColor(highlight)}>{label}</fc>'


def getLabel(label, large=True):
    return f'<fn={3 if large else 2}><fc={getColor(HL_LABEL)}>{label}</fc></fn>'


def getBox(label, theme=bfc.PALENIGHT):
    b = 3
    m = 1
    border = f'type=Left width={b}'
    margins = f'offset=C20 ml={m}'
    color = f'color={getColor(bfc.BASE01)}'
    padded = f' {label} '
    return f'<box {border} {margins} {color}>{padded}</box>  '


def getIcon(hexCode, large=True, theme=bfc.PALENIGHT):
    size = 2 if large else 3
    return f'<fc={getColor(bfc.BASE03)}><fn={size}>{hexCode}</fn></fc>'
