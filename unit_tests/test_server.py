"""
Написание unit-tests для функций сервера
"""
import unittest

from common.vars import *
from common.utils import *
from server import proc_client_message


class TestServer(unittest.TestCase):
    """
    Если все параметры сообщения переданы, то 200 : ОК
    Иначе -  400 : Bad Request
    """
    bad_request_answer = {RESPONSE: 400, ERROR: 'Bad Request'}

    def test_correct_request(self):
        """ 'эталонный' запрос"""
        client_data = {EVENT: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'Guest'}}
        self.assertEqual(proc_client_message(client_data), {RESPONSE: 200})

    def test_no_event(self):
        client_data = {TIME: 1, USER: {ACCOUNT_NAME: 'Guest'}}
        self.assertEqual(proc_client_message(client_data), self.bad_request_answer)

    def test_no_time(self):
        client_data = {EVENT: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}
        self.assertEqual(proc_client_message(client_data), self.bad_request_answer)

    def test_no_user(self):
        client_data = {EVENT: PRESENCE, TIME: 1}
        self.assertEqual(proc_client_message(client_data), self.bad_request_answer)

    def test_unknown_account(self):
        """Admin != Guest"""
        client_data = {EVENT: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'Admin'}}
        self.assertEqual(proc_client_message(client_data), self.bad_request_answer)


if __name__ == '__main__':
    unittest.main()
