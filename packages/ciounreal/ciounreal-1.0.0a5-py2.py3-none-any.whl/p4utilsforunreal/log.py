import sys
import logging


logger = None


def get_logger() -> logging.Logger:
    global logger
    if logger is None:
        logger = logging.getLogger('p4utils-for-unreal')
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.DEBUG)
    return logger
