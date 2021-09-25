import argparse
import select
import socket
import sys
import logging
import time

import logs.configs.server_log_config

from common.vars import *
from common.utils import *
from custom_decorators import log
from errors import IncorrectDataRecievedError

#  Создаем Logger с настроенным конфигом
Server_logger = logging.getLogger('server')


@log
def proc_client_message(message, messages_list, client):
    """
    Обрабатывает сообщения от клиента
    На вход подается сообщение (словарь)
    Проверяет корректность параметров, возвращает код-ответ в формате словаря
    """
    Server_logger.debug(f'Обработка сообщения от клиента: {message}')
    """
    Если сообщение о присутствии, обрабатываем и отвечаем.
    Если сообщение, добавляем в очередь.
    Иначе: BAD request!
    """
    if EVENT in message \
            and message[EVENT] == PRESENCE \
            and TIME in message \
            and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return

    elif EVENT in message \
            and message[EVENT] == MESSAGE \
            and TIME in message \
            and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return

    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


@log
def create_arg_parser():
    """
    парсер аргументов коммандной строки, для разбора переданных параметров
    :return:
    """
    parser = argparse.ArgumentParser(description='Обработка параметров запуска')
    parser.add_argument('-a', default='', nargs='?')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    return parser


def main():
    """
    явно указывать порт и ip-адрес можно используя параметры -p и -a
     Наример, server.py  -a 192.168.0.1 -p 8008
     В ином случае, будут использоваться DEFAULT_PORT и DEFAULT_IP_ADDRESS
    :return:
    """

    # клиентов, подключившихся к серверу, будем добавлять в список, сообщения от клиентов в очередь
    clients = []
    messages = []

    # списки для модуля select
    recv_lst = []
    send_lst = []
    err_lst = []

    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if listen_port < 1024 or listen_port > 65535:
        Server_logger.critical(f'Сервер запускается с недопустимого номера порта: {listen_port}.'
                               f'Диапазон адресов от 1024 до 65535. Подключение завершается...')
        sys.exit(1)

    Server_logger.info(f'Запущен сервер с парамертами: '
                       f' порт: {listen_port}, адрес для приема подключений: {listen_address}./'
                       f'Если адрес не указан, принимаются подключения со всех доступных адресов.')

    #  Сокет
    transport_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport_socket.bind((listen_address, listen_port))
    transport_socket.settimeout(1)

    # Слушаем порт
    transport_socket.listen(MAX_CONNECTIONS)

    """ Ждем подключения, если успешно, пишем в лог, добавляем клиента в список. """
    while True:
        try:
            client, client_address = transport_socket.accept()
        except OSError:
            pass
        else:
            Server_logger.info(f'Соедениние с клиентом {client_address} установлено.')
            clients.append(client)

        """ Проверяем наличие ждущих клиентов. """
        try:
            if clients:
                recv_lst, send_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        """ Принимаем сообщения 
            Если есть, добавляем в словарь  
            Если ошибка, исключаем клиента  """

        if recv_lst:
            for message_from_client in recv_lst:
                try:
                    proc_client_message(get_message(
                        message_from_client),
                        messages, message_from_client)
                except:
                    Server_logger.info(f'Клиент {message_from_client.getpeername()} '
                                       f' отключился от сервера.')
                    clients.remove(message_from_client)

        """Проверяем сообщения для отправки, 
        если есть ожидающие клиенты, они получат сообщение"""

        if messages and send_lst:
            message = {
                EVENT: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    Server_logger.info(f'Клиент {waiting_client.getpeername()}'
                                       f' отключился от сервера.')
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
