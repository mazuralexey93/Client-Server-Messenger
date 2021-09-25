""" Константы """

DEFAULT_PORT = 7777

DEFAULT_IP_ADDRESS = '127.0.0.1'

ENCODING = 'utf-8'

MAX_CONNECTIONS = 3  # Очередь подключений

MAX_PACKAGE_LENGTH = 1024  # Длина сообщения в байтах


""" Протокол JIM  (JSON instant messaging) """

EVENT = 'event'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
SENDER = 'sender'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
