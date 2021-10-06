import argparse
import socket
import sys
import json
import threading
import time
import logging
import logs.configs.client_log_config

from common.vars import *
from common.utils import *
from errors import ReqFieldMissingError, ServerError
from custom_decorators import log, Log

#  Создаем Logger с настроенным конфигом
Client_logger = logging.getLogger('client')


def print_help():
    """Функция выводящяя справку по использованию"""
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Получатель и текст будут запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        EVENT: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


##!
@log
def message_from_server(message, my_username):
    """ Функция, обрабатывающая сообщения других пользователей"""
    while True:
        try:
            if EVENT in message and message[EVENT] == MESSAGE \
                    and SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT and  message[DESTINATION] == my_username:
                print((f'\nПолучено сообщение от пользователя '
                       f'{message[SENDER]}: '
                       f'\n{message[MESSAGE_TEXT]}'))
                Client_logger.info(f'Получено сообщение от пользователя '
                                   f'{message[SENDER]}: '
                                   f'\n{message[MESSAGE_TEXT]}')
            else:
                Client_logger.error(f'Получено некорректное сообщение от сервера: {message}')
        except IncorrectDataRecievedError:
            Client_logger.error(f'Не удалось декодировать полученное сообщение.'
                                f' $%@^D!!**! <3')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            Client_logger.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает получателя и сообщение, отправляет на сервер"""
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение : ')
    message_dict = {
        EVENT: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    Client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        Client_logger.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        Client_logger.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@log
def user_actions(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения по команде пользователя.')
            Client_logger.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


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
    parser.add_argument('-n', '--name', default='None', nargs='?')
    return parser


def main():
    """
    Применяем параметры для клиента аналогично серверу
     Наример, client.py -a 192.168.0.1 -p 8008 -n client1
     Подгружаем параметры командной строки из парсера
     Проверяем параметры, при успешной попытке, равно как и при ошибке, пишем в логгер
    :return:
    """
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if server_port < 1024 or server_port > 65535:
        Client_logger.critical(f'Клиент пытается подключиться с недопустимого номера порта: {server_port}.'
                               f'Диапазон адресов от 1024 до 65535. Подключение завершается...')
        sys.exit(1)

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    Client_logger.info(f'Запущен клиент с парамертами:'
                       f' адрес сервера: {server_address}, '
                       f' порт: {server_port},'
                       f' имя пользователя: {client_name}')

    """Сообщаем о запуске"""
    print(f'Консольный месседжер. Клиентский модуль. Пользователь: {client_name}')

    """
    Инициализируем сокет, отправляем серверу сообщение о присутствии, 
    Хотим получит ответ от сервера
    Ответ пишем в логгер
    """
    try:
        transport_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport_socket.connect((server_address, server_port))
        send_message(transport_socket,  declare_presence(client_name))
        answer = proc_answer(get_message(transport_socket))
        Client_logger.info(f'Установлено собединение. Принят ответ от сервера {answer}')
        print(f'Установлено соединение с сервером.')
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
        """Если соединение установлено, запускаем процесс приема сообщений"""
        receiver = threading.Thread(target=message_from_server, args=(transport_socket, client_name))
        receiver.daemon = True
        receiver.start()

        """ Затем запускаем отправку сообщений, начинается взаимодействие с пользователем"""
        client_interface = threading.Thread(target=user_actions, args=(transport_socket, client_name))
        client_interface.daemon = True
        client_interface.start()
        Client_logger.debug('Запущены потоки')

        """ Каждую секунду проверяем, не завершен ли один из потоков.
        Если завершен, значит или был вызван 'exit' или потеряно соединение. """
        while True:
            time.sleep(1)
            if receiver.is_alive() and client_interface.is_alive():
                continue
            break

if __name__ == '__main__':
    main()
