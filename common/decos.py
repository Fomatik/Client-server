"""
1. Продолжая задачу логирования, реализовать декоратор @log, фиксирующий обращение к декорируемой функции.
Он сохраняет ее имя и аргументы.
2. В декораторе @log реализовать фиксацию функции, из которой была вызвана декорированная. Если имеется такой код:

@log
def func_z():
 pass

def main():
 func_z()

...в логе должна быть отражена информация:
"<дата-время> Функция func_z() вызвана из функции main"
"""
import inspect
import logging
import os
import sys
from functools import wraps

sys.path.append(os.path.join(os.path.dirname(__file__), '../log'))

from log import client_log_config
from log import server_log_config

if sys.argv[0].find('client.py') != -1:
    LOGGER = logging.getLogger('client')
else:
    LOGGER = logging.getLogger('server')


def log(func_to_log):
    @wraps(func_to_log)
    def log_writer(*args, **kwargs):
        call_func = func_to_log(*args, **kwargs)
        LOGGER.debug(f'Была вызвана функция {func_to_log.__name__} c параметрами {args}, {kwargs}. '
                     f'Вызов из модуля {func_to_log.__module__}. '
                     f'Вызов из функции {inspect.stack()[1][3]}')
        return call_func
    return log_writer