import logging
import sys
import os
sys.path.append('../')

"""
Конфигурация логгера для сервера
"""

# Подготовка имени файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

# Создаем экземпляр объекта класса Logger
Server_logger = logging.getLogger('server')
Server_logger.setLevel(logging.DEBUG)

# Формат сообщений: "<дата-время> <уровень_важности> <имя_модуля> <сообщение>"
s_formatter = logging.Formatter('%(asctime)-27s %(levelname)-12s %(filename)-24s %(message)s')

# Создаем обработчик логгирования для отладки, устанавливаем уровень важности, назначаем формат
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(s_formatter)
stream_handler.setLevel(logging.WARNING)


# Создать обработчик для вывода сообщений в лог-файл
file_handler = logging.FileHandler(PATH, encoding='utf-8')
file_handler.setFormatter(s_formatter)
file_handler.setLevel(logging.DEBUG)

# Добавляем в логгеры обработчики событий и устанавливаем уровень логгирования
Server_logger.addHandler(stream_handler)
Server_logger.addHandler(file_handler)
Server_logger.setLevel(logging.INFO)

# отладка
if __name__ == '__main__':
    Server_logger.info('Важная информация')
    Server_logger.debug('Отладочное сообщение')
    Server_logger.warning('Предупреждение!')
    Server_logger.error('Где-то ошибка!!')
    Server_logger.critical('Где-то БОЛЬШАЯ ошибка!!!')