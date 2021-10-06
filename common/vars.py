""" Константы """

DEFAULT_PORT = 6777

DEFAULT_IP_ADDRESS = '127.0.0.1'

ENCODING = 'utf-8'

MAX_CONNECTIONS = 3  # Очередь подключений

MAX_PACKAGE_LENGTH = 1024  # Длина сообщения в байтах


""" Протокол JIM  (JSON instant messaging) """

EVENT = 'event'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'

"""  Словари - ответы: """
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
