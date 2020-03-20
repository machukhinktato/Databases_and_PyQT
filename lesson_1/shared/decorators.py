"""decorators"""

import sys
import logging
import traceback
import logs.config_log_client_side
import logs.config_log_server_side


def log(useful_data):
    """decorator with logger which detecting on which side he is
    (server|client) and writes programs logs"""
    def writer_hands(*args, **kwargs):
        if sys.argv[0].find('client') == -1:
            logger_pen = logging.getLogger('server_side_logger')
        else:

            logger_pen = logging.getLogger('client_side_logger')
        note = useful_data(*args, **kwargs)
        logger_pen.debug(f'function {useful_data.__name__} '
                         f'with parameters: {args} and {kwargs}, '
                         f'from module {useful_data.__module__}, '
                         f'and function {traceback.format_stack()[0].strip().split()[-1]}.')
        return note

    return writer_hands
