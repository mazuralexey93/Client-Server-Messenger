import argparse
import dis
import select
import socket
import sys
import logging
import time
import types

import common.vars
import logs.configs.server_log_config
from common.vars import *
from common.utils import *
from custom_decorators import log
from db_conf import ServerDB
from errors import IncorrectDataReceivedError
from models import Base


class ServerVerifierMeta(type):

    def __init__(self, clsname, bases, clsdict):
        self.verify_socket(clsname, clsdict)
        type.__init__(self, clsname, bases, clsdict)

    @staticmethod
    def verify_socket(clsname, clsdict):
        socket_store = None
        for key, value in clsdict.items():
            if isinstance(value, socket.socket):
                raise Exception('Creating sockets in classes is forbidden')

            try:
                instructions = dis.get_instructions(value)
            except TypeError:
                continue

            for instruction in instructions:
                if instruction.argval == 'socket' and instruction.opname == 'LOAD_GLOBAL':
                    while instruction.opname != 'STORE_ATTR':
                        instruction = next(instructions)
                        if instruction.opname == 'LOAD_ATTR' and instruction.arg == 2:
                            if instruction.argval == 'SOCK_DGRAM':
                                raise Exception('UDP sockets is forbidden. Only TCP sockets is available ')
                    socket_store = instruction.argval

        if socket_store:
            forbidden_methods = ['connect']
            for key, value in clsdict.items():
                try:
                    instructions = dis.get_instructions(value)
                except TypeError:
                    continue

                for instruction in instructions:
                    if instruction == socket_store:
                        next_instruction = next(instruction)
                        if next_instruction.argval in forbidden_methods \
                                and next_instruction.opname == 'LOAD_ATTR':
                            raise Exception(f'{clsname} socket calls forbidden  method "{next_instruction.argval}".')


class PortVerifyDescriptor:
    def __init__(self):
        self._port = common.vars.DEFAULT_PORT

    def __get__(self, instance, owner=None):
        return self._port

    def __set__(self, instance, value):
        try:
            value = int(value)
            if not (0 <= value <= 65535):
                raise ValueError(f'Port should be an integer >= 0, <= 65535')
        except ValueError as e:
            print(f'Error {e}')
        setattr(instance, value)


class BaseServer(metaclass=ServerVerifierMeta):
    port = PortVerifyDescriptor()

    def __init__(self):
        self.server_logger = logging.getLogger('server')
        self.transport_socket = ''

    def start_server(self, address=DEFAULT_IP_ADDRESS):
        listen_address, listen_port = create_arg_parser()

        self.server_logger.info(f'Запущен сервер с парамертами: '
                                f' порт: {listen_port}, адрес для приема подключений: {listen_address}./'
                                f'Если адрес не указан, принимаются подключения со всех доступных адресов.')

        # клиентов, подключившихся к серверу, будем добавлять в список, сообщения от клиентов в очередь
        clients = []
        messages = []
        # списки для модуля select
        recv_lst = []
        send_lst = []
        err_lst = []
        # словарь, содержащий имена клиентов и их сокеты
        names = dict()

        self.transport_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport_socket.bind((address, self.port))
        self.transport_socket.settimeout(1)
        self.transport_socket.listen(MAX_CONNECTIONS)

        while True:
            try:
                client, client_address = self.transport_socket.accept()
                self.server_logger.info(f'Соедениние с клиентом {client_address} установлено.')
            except OSError:
                pass
            else:
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
                        proc_client_message(get_message(message_from_client),
                                            messages, message_from_client, clients, names)
                    except:
                        self.server_logger.info(f'Клиент {message_from_client.getpeername()} '
                                                f' отключился от сервера.')
                        clients.remove(message_from_client)

            """Если есть сообщения, обрабатываем"""
            for i in messages:
                try:
                    proc_message(i, names, send_lst)
                except Exception as e:
                    self.server_logger.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    no_user_dict = RESPONSE_400
                    no_user_dict[ERROR] = f'Пользователь {i[DESTINATION]} отклчился от сервера.'
                    send_message(names[i[SENDER]], no_user_dict)
                    del names[i[DESTINATION]]
            messages.clear()

    def init_db(self):
        db_name = DB_NAME
        self.db = ServerDB(Base, db_name)
        self.db.load()
        print(self.db.engine)


class ConcreteServer(BaseServer):
    pass


@log
def proc_client_message(message, messages_list, client, clients, names):
    """
    Обрабатывает сообщения от клиента
    На вход подается сообщение (словарь)
    Проверяет корректность параметров, возвращает код-ответ в формате словаря.
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
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
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

    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError


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


if __name__ == '__main__':
    server = ConcreteServer()
    server.start_server()
