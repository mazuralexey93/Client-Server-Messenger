import json
from common.vars import *
from custom_decorators import log
from errors import NonDictInputError, IncorrectDataReceivedError

"""
Общие функции для клиента и для сервера
словарь(сообщение) -> json строка -> байты
"""


@log
def get_message(sock):
    """
    Принимает и декодирует сообщение
    Преобразует байты в словарь,
    Если на входе не байты - выдает ошибку
    :param sock:
    :return:
    """

    encoded_response = sock.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataReceivedError
    raise IncorrectDataReceivedError


@log
def send_message(sock, message):
    """
    Кодирует и отправляет сообщение
    Принимает словарь и отправляет его
    :param sock:
    :param message:
    :return:
    """
    if not isinstance(message, dict):
        raise NonDictInputError
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)
