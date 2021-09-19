import argparse
import socket
import sys
import logging
import logs.configs.server_log_config

from common.vars import *
from common.utils import *
from custom_decorators import log
from errors import IncorrectDataRecievedError

#  Создаем Logger с настроенным конфигом
Server_logger = logging.getLogger('server')


@log
def proc_client_message(message):
    """
    Обрабатывает сообщения от клиента
    На вход подается сообщение (словарь)
    Проверяет корректность параметров, возвращает код-ответ в формате словаря
    :param message:
    :return:
    """
    Server_logger.debug(f'Обработка сообщения от клиента: {message}')
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


@log
def main():
    """
    явно указывать порт и ip-адрес можно используя параметры -p и -a
     Наример, server.py  -a 192.168.0.1 -p 8008
     В ином случае, будут использоваться DEFAULT_PORT и DEFAULT_IP_ADDRESS
    :return:
    """

    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if listen_port < 1024 or listen_port > 65535:
        Server_logger.critical(f'Сервер запускается с недопустимого номера порта: {listen_port}.'
                               f'Диапазон адресов от 1024 до 65535. Подключение завершается...')
        sys.exit(1)

    Server_logger.info('fЗапущен сервер с парамертами: '
                       f' порт: {listen_port}, адрес для приема подключений: {listen_address}./'
                       f'Если адрес не указан, принимаются подключения со всех доступных адресов.')

    #  Сокет
    transport_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport_socket.bind((listen_address, listen_port))

    # Слушаем порт
    transport_socket.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport_socket.accept()
        Server_logger.info(f'Соедениние с клиентом {client_address} установлено.')
        try:
            message_from_client = get_message(client)
            Server_logger.debug(f'Получено сообщение {message_from_client}')
            response = proc_client_message(message_from_client)
            Server_logger.debug(f'Сформирован ответ клиенту {response}')
            send_message(client, response)
            Server_logger.info(f'Соедениние с клиентом {client_address} закрывается..')
            client.close()
        except json.JSONDecodeError:
            Server_logger.error(f'Не удалось декодировать JSON-строку, принятую от клиента {client_address}'
                                'fСоедениние с клиентом закрывается..')
            client.close()
        except IncorrectDataRecievedError:
            Server_logger.error(f'От клиента {client_address} приняты некорректные данные. '
                                'fСоедениние с клиентом закрывается..')
            client.close()


if __name__ == '__main__':
    main()
