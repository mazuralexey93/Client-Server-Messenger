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
def proc_client_message(message, messages_list, client, clients, names):
    """
    Обрабатывает сообщения от клиента
    На вход подается сообщение (словарь)
    Проверяет корректность параметров, возвращает код-ответ в формате словаря
    """

    Server_logger.debug(f'Обработка сообщения от клиента: {message}')
    """
    Если сообщение о присутствии, обрабатываем и отвечаем.
    Если пользователь не зарегистрирован, регистрируем. 
    Иначе - отправляем ответ и завершаем соединение.
    Если сообщение, добавляем в очередь.
    Если клиент выходит, удаляем информаию о нем.
    """
    if EVENT in message \
            and message[EVENT] == PRESENCE \
            and TIME in message \
            and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя занято, попробуйте другое.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return

    elif EVENT in message \
            and message[EVENT] == MESSAGE \
            and SENDER in message \
            and DESTINATION in message \
            and TIME in message \
            and MESSAGE_TEXT in message:
        messages_list.append(message)
        return

    elif EVENT in message \
            and message[EVENT] == EXIT \
            and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return

    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


def proc_message(message, names, listen_socks):
    """
    Функция  отправки сообщения определённому клиенту. Принимает сообщение(словарь),
    список зарегистрированых пользователей и слушающие сокеты.
    Если есть клиенты ожидающие подключения, сокеты подключены,  отправляем сообщение, пишем в лог
    Если клиент отключился или заданы неверные параметры - вызов ошибки и запись в лог.
    """
    if message[DESTINATION] in names \
            and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        Server_logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                           f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        Server_logger.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован, '
            f'отправка сообщения невозможна.')


@log
def create_arg_parser():
    """
    парсер аргументов коммандной строки, для разбора переданных параметров
    """
    parser = argparse.ArgumentParser(description='Обработка параметров запуска')
    parser.add_argument('-a', default='', nargs='?')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


def main():
    """
    явно указывать порт и ip-адрес можно используя параметры -p и -a
     Наример, server.py  -a 192.168.0.1 -p 8008
     В ином случае, будут использоваться DEFAULT_PORT и DEFAULT_IP_ADDRESS
    """

    # клиентов, подключившихся к серверу, будем добавлять в список, сообщения от клиентов в очередь
    clients = []
    messages = []

    # словарь, содержащий имена клиентов и их сокеты
    names = dict()

    listen_address, listen_port = create_arg_parser()

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

        # списки для модуля select
        recv_lst = []
        send_lst = []
        err_lst = []
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
                    proc_client_message(get_message(message_from_client),
                                        messages, message_from_client)
                except:
                    Server_logger.info(f'Клиент {message_from_client.getpeername()} '
                                       f' отключился от сервера.')
                    clients.remove(message_from_client)

        # """Проверяем сообщения для отправки,
        # если есть ожидающие клиенты, они получат сообщение"""
        #
        # if messages and send_lst:
        #     message = {
        #         EVENT: MESSAGE,
        #         SENDER: messages[0][0],
        #         TIME: time.time(),
        #         MESSAGE_TEXT: messages[0][1]
        #     }
        #     del messages[0]
        #     for waiting_client in send_lst:
        #         try:
        #             send_message(waiting_client, message)
        #         except:
        #             Server_logger.info(f'Клиент {waiting_client.getpeername()}'
        #                                f' отключился от сервера.')
        #             clients.remove(waiting_client)

        """Если есть сообщения, обрабатываем"""
        for i in messages:
            try:
                proc_message(i, names, send_lst)
            except Exception:
                Server_logger.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                no_user_dict = RESPONSE_400
                no_user_dict[ERROR] = f'Пользователь {i[DESTINATION]} отклчился от сервера.'
                send_message(names[i[SENDER]], no_user_dict)
                # clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()
