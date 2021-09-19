import inspect
import logging
import sys
import traceback

import logs.configs.client_log_config
import logs.configs.server_log_config

"""
В зависимости от того, из какого модуля вызвана функция, будут применяться конфиги для сервера или клиента.
# Метод find () возвращает индекс первого вхождения искомой подстроки,
# если он найден в данной строке.
# Если его не найдено, - возвращает -1.
# os.path.split(sys.argv[0])[1]
"""
if sys.argv[0].find('client') == -1:
    Universal_logger = logging.getLogger('server')
else:
    Universal_logger = logging.getLogger('client')


def log(func):
    """
    Декоратор, логирующий работу кода.
    """

    def wrapper(*args, **kwargs):
        """ функция-обертка """
        res = func(*args, **kwargs)
        """ искомая функция """
        Universal_logger.debug(f'Вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
                               f'Вызов из модуля {func.__module__}. '
                               f'Вызов из функции {inspect.stack()[1][3]}')
        return res

    return wrapper
