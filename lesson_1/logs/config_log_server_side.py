"""Server side log configurator"""

import sys
import os
import logging
import logging.handlers

sys.path.append('../')
from shared.variables import LOGGING_LEVEL

SERVER_SIDE_FORMATTER = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(message)s')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server_side.log')
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_SIDE_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
SERVER_LOG_FILE = logging.handlers.TimedRotatingFileHandler(
    PATH, encoding='utf8', interval=1, when='D')
SERVER_LOG_FILE.setFormatter(SERVER_SIDE_FORMATTER)
LOGGER = logging.getLogger('server_side_logger')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(SERVER_LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Critical error')
    LOGGER.error('Error')
    LOGGER.debug('Debug information')
    LOGGER.info('Info message')
