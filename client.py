import argparse
import socket
import sys
import json
import time
import logging
import logs.configs.client_log_config

from common.vars import *
from common.utils import *
from errors import ReqFieldMissingError, ServerError
from custom_decorators import log, Log

#  Создаем Logger с настроенным конфигом
Client_logger = logging.getLogger('client')


@log
def message_from_server(message):
    """ Функция, обрабатывающая сообщения других пользователей"""
    if EVENT in message and message[EVENT] == MESSAGE \
            and SENDER in message and MESSAGE_TEXT in message:
        print((f'Получено сообщение от пользователя '
               f'{message[SENDER]}: '
               f'{message[MESSAGE_TEXT]}'))
        Client_logger.info(f'Получено сообщение от пользователя '
                           f'{message[SENDER]}: '
                           f'{message[MESSAGE_TEXT]}')
    else:
        Client_logger.error(f'Получено некорректное сообщение от сервера: {message}')


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает словарь сообщения и возвращает его.
    Опционально, по команде можно выйти.
    """
    message = input('Введите сообщение для отправки или \'exit\' для завершения работы: ')
    if message.lower() == 'exit':
        sock.close()
        Client_logger.debug('Клиент завершил работу по команде "exit"...')
        sys.exit(0)

    message_dict = {
        EVENT: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    Client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


@log
def declare_presence(account_name='Guest'):
    """   Генерирует запрос о присутствии клиента Oneline """

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


@log
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


@log
def create_arg_parser():
    """
    парсер аргументов коммандной строки, для разбора переданных параметров
    :return:
    """
    parser = argparse.ArgumentParser(description='Обработка параметров запуска')
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
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
    client_mode = namespace.mode

    if server_port < 1024 or server_port > 65535:
        Client_logger.critical(f'Клиент пытается подключиться с недопустимого номера порта: {server_port}.'
                               f'Диапазон адресов от 1024 до 65535. Подключение завершается...')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        Client_logger.critical(f'Указан недопустимый режим работы {client_mode}, '
                               f'Допустимо : listen (прием сообщений) или  send (отправка сообщений)')
        sys.exit(1)

    Client_logger.info(f'Запущен клиент с парамертами:'
                       f' адрес сервера: {server_address}, '
                       f' порт: {server_port},'
                       f' режим работы: {client_mode}')

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
        Client_logger.info(f'Установлено собединение. Принят ответ от сервера {answer}')
        print(f'Установлено соединение с сервером.')
        # print(answer)
    except (ValueError, json.JSONDecodeError):
        Client_logger.error('Не удалось декодировать сообщение сервера.')
        sys.exit(1)
    except ServerError as error:
        Client_logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_field_error:
        Client_logger.error(f'В ответе сервера отсутствует необходимое поле: '
                            f'{missing_field_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        Client_logger.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                               f'В подключении отказано.')
        sys.exit(1)

    else:
        """
        Если соединение установлено, работаем согласно режиму:
        На отправку или прием сообщений
        """
        if client_mode == 'listen':
            print('Режим работы - приём сообщений.')
        else:
            print('Режим работы - отправка сообщений.')

        while True:

            if client_mode == 'send':
                try:
                    send_message(transport_socket, create_message(transport_socket))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    Client_logger.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    message_from_server(get_message(transport_socket))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    Client_logger.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
