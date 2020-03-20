"""Configuration for log of client side """

import sys
import os
import logging

sys.path.append('../')
from shared.variables import LOGGING_LEVEL

CLIENT_SIDE_FORMATTER = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(message)s')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client_side.log')
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_SIDE_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
CLIENT_LOG_FILE = logging.FileHandler(PATH, encoding='utf8')
CLIENT_LOG_FILE.setFormatter(CLIENT_SIDE_FORMATTER)
LOGGER = logging.getLogger('client_side_logger')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(CLIENT_LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Critical error')
    LOGGER.error('Error')
    LOGGER.debug('Debug information')
    LOGGER.info('Info message')
