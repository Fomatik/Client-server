"""
Unittest для функций клиента
"""
import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../common'))

from client import create_presence, process_answer
from common.setting import ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, PRESENCE


class TestClient(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_presence_msg(self):
        """ Тест формирования PRESENCE сообщения без параметров """
        msg = create_presence()
        msg[TIME] = 1.1
        self.assertEqual(msg, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_presence_msg_with_param(self):
        """ Тест формирования PRESENCE сообщения с параметром 'User' """
        account_name = 'User'
        msg = create_presence(account_name)
        msg[TIME] = 1.1
        self.assertEqual(msg, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'User'}})

    def test_answer_200(self):
        """ Тест обработки 200-го ответа от сервера """
        self.assertEqual(process_answer({RESPONSE: 200}), '200: OK')

    def test_answer_400(self):
        """ Тест обработки 400-го ответа от сервера """
        self.assertEqual(process_answer({RESPONSE: 400, ERROR: 'BadRequest'}), '400: BadRequest')

    def test_another_answer(self):
        """ Тест обработки исключения ответа сообщения"""
        message = {'_'}
        self.assertRaises(ValueError, process_answer, message)


if __name__ == '__main__':
    unittest.main()
