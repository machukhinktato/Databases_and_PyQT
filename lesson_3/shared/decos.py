""" decorators """
import sys
import logs.config_server_log
import logs.config_client_log
import logging

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


def log(func_to_log):
    def log_saver(*args , **kwargs):
        logger.debug(f'called function {func_to_log.__name__} '
                     f'with params {args} , {kwargs}. Call from'
                     f' module {func_to_log.__module__}')
        ret = func_to_log(*args , **kwargs)
        return ret
    return log_saver