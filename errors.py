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

