"""Configuration for log of server side """
import sys
import logging
import logging.handlers
import os

sys.path.append('../')
from shared.variables import LOGGING_LEVEL

SERVER_FORMATTER = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(message)s')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.INFO)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(
    PATH, encoding='utf8', interval=1, when='D')
LOG_FILE.setFormatter(SERVER_FORMATTER)

LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Critical error')
    LOGGER.error('Error')
    LOGGER.debug('Debug information')
    LOGGER.info('Info message')
