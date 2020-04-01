""" descriptors """
import logging
import sys


if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('server')


# port descriptor
class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f'attmept to launch server with unreachable value '
                f'{value}, range allowed: 1024 - 65535')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

