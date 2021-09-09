"""
Написание unit-tests для функций клиента
"""
import unittest

from common.vars import *
from common.utils import *
from client import declare_presense, proc_answer


class TestClient(unittest.TestCase):

    def test_presence(self):
        """ 'эталонный' запрос"""
        test_func = declare_presense()
        test_func[TIME] = 1  # искусственно назначаем время, для корректности выражения, иначе ошибка
        client_data = {EVENT: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'Guest'}}
        self.assertEqual(test_func, client_data)

    def test_answer_200(self):
        """тест корректного ответа 200"""
        self.assertEqual(proc_answer({RESPONSE: 200}), '200 : OK')

    def test_answer_400(self):
        """тест корректного ответа 400"""
        self.assertEqual(proc_answer({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_answer_missing_response(self):
        """Тест без поля RESPONSE"""
        self.assertRaises(ValueError, proc_answer, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
