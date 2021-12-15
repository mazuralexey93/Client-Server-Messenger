"""
Файл для пользовательских исключений и ошибок
"""


class ReqFieldMissingError(Exception):
    """
    Ошибка: В принятом словаре присутствуют не все необходимые поля!
    """

    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}.' \
               f' Проверьте, все ли поля переданы.'


class IncorrectDataReceivedError(Exception):
    """
    Исключение: в сокет пришли некорректные данные
    """

    def __str__(self):
        return 'Принято некорректное сообщение. $%@^D!!**! <3'


class NonDictInputError(Exception):
    """
    Исключение: Аргумент функции должен быть словарём.
    """

    def __str__(self):
        return 'Аргумент функции должен быть словарём. Проверьте тип данных аргументов.'


class ServerError(Exception):
    """Исключение: ошибка на стророне сервера"""

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class ServerDBError(Exception):
    """Исключение: ошибка на стороне БД"""
    pass
