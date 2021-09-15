import socket
import sys
import json

from common.vars import *
from common.utils import *


def proc_client_message(message):
    """
    Обрабатывает сообщения от клиента
    На вход подается сообщение (словарь)
    Проверяет корректность параметров, возвращает код-ответ в формате словаря
    :param message:
    :return:
    """

    if EVENT in message \
            and message[EVENT] == PRESENCE \
            and TIME in message \
            and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    else:
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }


def main():
    """
    явно указывать порт и ip-адрес можно используя параметры -p и -a
     Наример, server.py  -a 192.168.0.1 -p 8008
     В ином случае, будут использоваться DEFAULT_PORT и DEFAULT_IP_ADDRESS
    :return:
    """

    #  назначаем порт
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' укажите номер порта.')
        sys.exit(1)
    except ValueError:
        print('Укажите порт числом от 1024 до 65535.')
        sys.exit(1)

    #  назначаем ip-адрес
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            # listen_address = DEFAULT_IP_ADDRESS
            listen_address = ''  # для всех доступных адресов

    except IndexError:
        print(
            'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    #  Сокет
    transport_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport_socket.bind((listen_address, listen_port))

    # Слушаем порт
    transport_socket.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport_socket.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)

            response = proc_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Клиент отправил некорректное сообщение!')
            client.close()


if __name__ == '__main__':
    main()
