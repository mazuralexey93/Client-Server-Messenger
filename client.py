import argparse
import socket
import sys
import json
import time
import logging
import logs.configs.client_log_config

from common.vars import *
from common.utils import *
from errors import ReqFieldMissingError
from custom_decorators import log, Log

#  Создаем Logger с настроенным конфигом
Client_logger = logging.getLogger('client')


@Log()
def declare_presence(account_name='Guest'):
    """
    Генерирует запрос о присутствии клиента Oneline
    EVENT == presence
    :param account_name:
    :return:
    """

    client_data = {
        EVENT: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name

        }
    }
    #  Пишем в лог
    Client_logger.debug(f'Пользователь {account_name} теперь онлайн: отправил сообщение о({PRESENCE})')
    return client_data


@Log()
def proc_answer(message):
    """
    Обрабатывает сообщения от сервера
    возвращает код-ответ в формате словаря
    Если все парамерты переданы, 200 : ОК
    Иначе 400 : Bad Request
    :param message:
    :return:
    """
    Client_logger.debug(f'Обработка сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


@Log()
def create_arg_parser():
    """
    парсер аргументов коммандной строки, для разбора переданных параметров
    :return:
    """
    parser = argparse.ArgumentParser(description='Обработка параметров запуска')
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    return parser


def main():
    """
    Применяем параметры для клиента аналогично серверу
     Наример, client.py -a 192.168.0.1 -p 8008
     Подгружаем параметры командной строки из парсера
     Проверяем параметры, при успешной попытке, равно как и при ошибке, пишем в логгер
    :return:
    """
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port

    if server_port < 1024 or server_port > 65535:
        Client_logger.critical(f'Клиент пытается подключиться с недопустимого номера порта: {server_port}.'
                               f'Диапазон адресов от 1024 до 65535. Подключение завершается...')
        sys.exit(1)

    Client_logger.info(f'Запущен клиент с парамертами: '
                       f'адрес сервера: {server_address}, порт: {server_port}')

    """
    Инициализируем сокет, отправляем серверу сообщение о присутствии, 
    Хотим получит ответ от сервера
    Ответ пишем в логгер
    """
    try:
        transport_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport_socket.connect((server_address, server_port))
        message_to_server = declare_presence()
        send_message(transport_socket, message_to_server)
        answer = proc_answer(get_message(transport_socket))
        Client_logger.info(f'Принят ответ от сервера {answer}')
        print(answer)
    except (ValueError, json.JSONDecodeError):
        Client_logger.error('Не удалось декодировать сообщение сервера.')
    except ReqFieldMissingError as missing_field_error:
        Client_logger.error(f'В ответе сервера отсутствует необходимое поле: '
                            f'{missing_field_error.missing_field}')
    except ConnectionRefusedError:
        Client_logger.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                               f'В подключении отказано.')


if __name__ == '__main__':
    main()
