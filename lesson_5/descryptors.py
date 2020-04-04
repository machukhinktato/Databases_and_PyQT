import logging
import sys

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


# port descriptor:
class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f'attempt to launch with incorret port number {value}.'
                f' alloweed value in range between 1024 and 65535.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
