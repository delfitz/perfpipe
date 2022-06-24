import utils.base16Colors as bfc
from utils.sparkUtils import getHighlight

HL_LABEL = bfc.BASE04
HL_LABEL_SUB = bfc.BASE03
HL_ICON = bfc.BASE04

TEXT_SMALL = 1
TEXT_MEDIUM = 2
TEXT_LARGE = 3

ICON_SMALL = 6
ICON_MEDIUM = 7
ICON_LARGE = 8


def getColor(base, theme):
    if not theme:
        theme = bfc.PALENIGHT
    return bfc.getTheme(theme)[base]


def getIcon(icon, size=ICON_MEDIUM, theme=None):
    return f'<fn={size}><fc={getColor(HL_ICON, theme)}>{icon}</fc></fn>'


def formatLabel(label, sub=False, icon=None, theme=None):
    iconLabel = getIcon(icon, theme=theme) + ' ' if icon else ''
    size, color = (TEXT_SMALL, HL_LABEL_SUB) if sub else (TEXT_LARGE, HL_LABEL)
    textLabel = f'<fn={size}><fc={getColor(color, theme)}>{label}</fc></fn>'
    return f'{iconLabel}{textLabel}'


def formatStat(level,
               unit='%',
               decimals=1,
               label=None,
               highlight=False,
               hl_splits=None,
               icon=None,
               theme=None):
    statLabel = f'{label}' if label else ''
    statLine = f'{statLabel} {level:.{decimals}f}<fn=1>{unit}</fn>'
    color = getHighlight(level, hl_splits, theme) if highlight else getColor(
        HL_LABEL, theme)
    if icon:
        iconLabel = getIcon(icon, theme=theme) if icon else ''
        return f'<fn=2><fc={color}>{iconLabel} {statLine}</fc></fn>'
    else:
        return f'<fn=2><fc={color}>{statLine}</fc></fn>'


def formatClock(dt, icon, theme=None):
    timeLabel = f'<fn=3>{dt:%-I:%M}<fn=1>{dt:%p}</fn></fn>'
    iconLabel = f' <fn=8><fc={getColor(HL_ICON, theme)}>{icon}</fc></fn>  '
    dateLabel = f'{dt:%A, %B %-d}'
    clockLabel = f'{timeLabel} {iconLabel} {dateLabel}'
    formatted = f'<fn=2><fc={getColor(HL_LABEL, theme)}>{clockLabel}</fc></fn>'
    return formatted


def formatWeather(temp,
                  icon=None,
                  date=None,
                  unit=None,
                  hl_splits=None,
                  theme=None):
    tempFont = 2 if date else 3
    iconFont = 6 if date else 7

    hourLabel = f'<fn=1><fc={getColor(HL_LABEL, theme)}>{date:%-I%p}</fc></fn>' if date else ''
    tempUnit = f'{temp:.0f}'
    tempLabel = f'<fn={tempFont}><fc={getHighlight(temp, hl_splits, theme)}>{tempUnit}</fc></fn>'
    iconLabel = f'<fn={iconFont}><fc={getColor(HL_ICON, theme)}>{icon}</fc></fn>'
    return f'{tempLabel}{iconLabel}{hourLabel}'
