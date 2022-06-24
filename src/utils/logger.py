import logging

FMT = '[%(asctime)s.%(msecs)03d] %(levelname)s %(module)s.%(funcName)s => %(message)s'
DATE_FMT = '%H:%M:%S'


def logConfig(level=logging.INFO, file=None):
    if file:
        logging.basicConfig(level=level,
                            filename=file,
                            encoding='utf-8',
                            format=FMT,
                            datefmt=DATE_FMT)
    else:
        logging.basicConfig(level=level, format=FMT, datefmt=DATE_FMT)
