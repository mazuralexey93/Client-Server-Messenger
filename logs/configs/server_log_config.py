import logging.handlers
import sys
import os

"""
Конфигурация логгера для сервера:
Форматтер
Обработчик
Логгер
Настройки
"""

# Подготовка имени файла
sys.path.append('../')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

# Формат сообщений: "<дата-время> <уровень_важности> <имя_модуля> <сообщение>"
s_formatter = logging.Formatter('%(asctime)-27s %(levelname)-12s %(filename)-24s %(message)s')

# Создаем обработчик логгирования для отладки, устанавливаем уровень важности, назначаем формат
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(s_formatter)
stream_handler.setLevel(logging.ERROR)

"""
TimedRotatingFileHandler
В аргументе interval передается число,
определяющее величину интервала в единицах, а в when — строка,
определяющая единицы измерения.
Допустимыми значениями для аргумента when являются:
S (секунды), M (минуты), H (часы), D (дни), W (недели) и midnight (ротация выполняется в полночь).
Самые "свежие" логи сохранятся в файле server.log, остальные будут журналироваться по ротации в отдельные файлы.
"""

file_handler = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8',
                                                         interval=1, when='midnight')
file_handler.setFormatter(s_formatter)
file_handler.setLevel(logging.DEBUG)

# Создаем экземпляр объекта класса Logger
Server_logger = logging.getLogger('server')

# Добавляем в логгеры обработчики событий и устанавливаем уровень логгирования
Server_logger.addHandler(stream_handler)
Server_logger.addHandler(file_handler)
Server_logger.setLevel(logging.DEBUG)

# отладка
if __name__ == '__main__':
    Server_logger.info('Важная? информация')
    Server_logger.debug('Отладочное сообщение')
    Server_logger.warning('Предупреждение!')
    Server_logger.error('Где-то ошибка!!')
    Server_logger.critical('Где-то БОЛЬШАЯ ошибка!!!')
