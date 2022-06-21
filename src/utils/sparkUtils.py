import utils.base16Colors as bfc

HL_INACTIVE = bfc.BASE02
HL_LOW = bfc.BASE03
HL_MODERATE = bfc.BASE0D
HL_ACTIVE = bfc.BASE0A
HL_HIGH = bfc.BASE09
HL_CRITICAL = bfc.BASE08

SPARK_CHARS = u'▁▁▂▃▄▅▆▇█'
SPARK_SPLITS = [0.0, 1, 2, 3, 5, 10, 50, 90]

HL_COLORS = [HL_INACTIVE, HL_LOW, HL_MODERATE, HL_ACTIVE, HL_HIGH, HL_CRITICAL]
HL_SPLITS = [0.1, 3, 10, 50, 90]


def bucket(value, splits):
    for idx, split in enumerate(splits):
        if splits[0] > splits[-1]:
            if value >= split:
                return idx
        else:
            if value <= split:
                return idx
    return len(splits)


def getHighlight(level, splits, theme):
    if not theme:
        theme = bfc.PALENIGHT
    if not splits:
        splits = HL_SPLITS
    return bfc.getTheme(theme)[HL_COLORS[bucket(level, splits)]]


def getSparkChar(level, splits):
    return SPARK_CHARS[bucket(level, splits)]


def getSparkline(levels,
                 hl_splits=HL_SPLITS,
                 spark_splits=SPARK_SPLITS,
                 theme=None):
    sparkline = ''
    for level in levels:
        color = getHighlight(level, hl_splits, theme)
        spark = getSparkChar(level, spark_splits)
        sparkline += f'<fc={color}>{spark}</fc>'
    return f'<fn=1>{sparkline}</fn>'
