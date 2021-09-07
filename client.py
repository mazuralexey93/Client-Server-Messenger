import socket
import sys
import json
import time

from common.vars import *
from common.utils import *


def declare_presense(account_name='Guest'):
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
    return client_data


def proc_answer(message):
    """
    Обрабатывает сообщения от сервера
    возвращает код-ответ в формате словаря
    Если все парамерты переданы, 200 : ОК
    Иначе 400 : Bad Request
    :param message:
    :return:
    """

    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    """
    Применяем параметры для клиента аналогично серверу
     Наример, client.py -a 192.168.0.1 -p 8008
    :return:
    """
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('Укажите порт числом от 1024 до 65535.')
        sys.exit(1)

    """
    Инициализируем сокет, отправляем серверу сообщение о присутствии, 
    Хотим получит ответ от сервера
    """

    transport_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport_socket.connect((server_address, server_port))
    message_to_server = declare_presense()
    send_message(transport_socket, message_to_server)
    try:
        answer = proc_answer(get_message(transport_socket))
        print(answer)
    except \
            (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
