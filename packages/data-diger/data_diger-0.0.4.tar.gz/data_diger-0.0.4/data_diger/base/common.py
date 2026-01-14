import os
import logging


def log(name, filename=None):
    format = '%(asctime)s : %(process)d : %(lineno)d : %(name)s : %(levelname)s : %(message)s'
    # создаём logger
    logger = logging.getLogger(name)

    if os.environ.get('BASIC_LOG_LEVEL'):
        logging.basicConfig(
            level=int(os.environ.get('BASIC_LOG_LEVEL')),
            format=format
        )

    logger.setLevel(int(os.environ.get('LOGGING_LEVEL', 10)))
    logger.propagate = False

    # создаём консольный handler и задаём уровень
    if filename:
        ch = logging.FileHandler(filename)
    else:
        ch = logging.StreamHandler()

    # создаём formatter
    formatter = logging.Formatter(format)
    # %(lineno)d :
    # добавляем formatter в ch
    ch.setFormatter(formatter)

    # добавляем ch к logger
    logger.addHandler(ch)

    # logger.debug('debug message')
    # logger.info('info message')
    # logger.warn('warn message')
    # logger.error('error message')
    # logger.critical('critical message')
    return logger
