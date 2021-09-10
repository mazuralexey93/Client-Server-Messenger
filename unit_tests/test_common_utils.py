"""
Написание unit-tests для общих утилит
"""
import unittest
import json
from common.vars import *
from common.utils import *


class TestEmulationSocket:
    """
    Для корректного тестирования функций отправки и приема сообщений необходим сокет
    В этом тестовом классе создается словарь, который будет использоваться при тестировании
    """

    def __init__(self, socket_dict):
        self.socket_dict = socket_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_send_to_sock):
        """
        Кодируем сообщение
        Сохраняем, что должно быть отправлено в сокет
        Отправляем
        :param message_send_to_sock:
        """

        test_json_message = json.dumps(self.socket_dict)
        self.encoded_message = test_json_message.encode(ENCODING)
        self.received_message = message_send_to_sock

    def recv(self, max_len):
        """
        Принимаем данные из сокета
        :return:
        """
        test_json_message = json.dumps(self.socket_dict)
        return test_json_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    """
    Написание unit-tests для общих функций
    """

    test_client_data = {EVENT: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'test_Guest'}}
    test_ok_answer = {RESPONSE: 200}
    test_err_answer = {RESPONSE: 400, ERROR: 'Bad Request'}

    def test_send_message(self):
        """
        Используем тестовый сокет
        Создаем экземпляр тестового словаря
        Проверяем корректность ф-ии отправки
        Сравниваем результат кодирования и тестовой ф-ии
        Также проверим исключение, если на входе не словарь
        """

        test_socket = TestEmulationSocket(self.test_client_data)
        send_message(test_socket, self.test_client_data)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)
        with self.assertRaises(Exception):
            send_message(test_socket, test_socket)

    def test_get_message(self):
        """
        Создаем экземпляры словарей ответа при корректных данных и при ошибке
        """
        test_sock_ok = TestEmulationSocket(self.test_ok_answer)
        test_sock_err = TestEmulationSocket(self.test_err_answer)
        self.assertEqual(get_message(test_sock_ok), self.test_ok_answer)
        self.assertEqual(get_message(test_sock_err), self.test_err_answer)


if __name__ == '__main__':
    unittest.main()
