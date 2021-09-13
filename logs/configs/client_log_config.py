import logging
import sys
import os
sys.path.append('../')

"""
Конфигурация логгера для клиентов
"""

# Подготовка имени файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

# Создаем экземпляр объекта класса Logger
Client_logger = logging.getLogger('client')
Client_logger.setLevel(logging.INFO)

# Формат сообщений: "<дата-время> <уровень_важности> <имя_модуля> <сообщение>"
c_formatter = logging.Formatter('%(asctime)-27s %(levelname)-12s %(filename)-24s %(message)s')

# Создаем обработчик логгирования для отладки, устанавливаем уровень важности, назначаем формат
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(c_formatter)
stream_handler.setLevel(logging.WARNING)


# Создать обработчик для вывода сообщений в лог-файл
file_handler = logging.FileHandler(PATH, encoding='utf-8')
file_handler.setFormatter(c_formatter)
file_handler.setLevel(logging.INFO)

# Добавляем в логгеры обработчики событий и устанавливаем уровень логгирования
Client_logger.addHandler(stream_handler)
Client_logger.addHandler(file_handler)


# отладка
if __name__ == '__main__':
    Client_logger.info('Важная информация')
    Client_logger.debug('Отладочное сообщение')
    Client_logger.warning('Предупреждение!')
    Client_logger.error('Где-то ошибка!!')
    Client_logger.critical('Где-то БОЛЬШАЯ ошибка!!!')
