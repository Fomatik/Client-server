"""
Unittest для функций сервера
Тесты оказались полезны. Пришлось поправить функцию.
"""
import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))

from server_old import process_client_message
from common.setting import SERVER_IP, SERVER_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, \
    RESPONSE, ERROR


class TestServer(unittest.TestCase):
    def setUp(self) -> None:
        """ Формируем валидный запрос от клиента """
        self.norm = {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }

        self.bad_request = {RESPONSE: 400, ERROR: 'BadRequest'}

    def tearDown(self) -> None:
        pass

    def test_server_answer_for_client(self):
        """ Тест 200-го ответа сервера на валидный запрос """
        self.assertEqual(process_client_message(self.norm), {RESPONSE: 200})

    def test_server_error_without_name(self):
        """ Тест 400-го ответа сервера на запрос без имени пользователя """
        self.norm[USER][ACCOUNT_NAME] = ''
        self.request_ = {RESPONSE: 400, ERROR: 'BadRequest'}
        self.assertEqual(process_client_message(self.norm), self.bad_request)

    def test_server_error_null_request(self):
        """ Тест 400-го ответа сервера на пустой запрос """
        self.norm = {}
        self.assertEqual(process_client_message(self.norm), self.bad_request)

    def test_server_error_action(self):
        """ Тест 400-го ответа сервера на неизвестное действие """
        self.norm[ACTION] = 'Error'
        self.assertEqual(process_client_message(self.norm), self.bad_request)

    def test_server_error_time(self):
        """ Тест 400-го ответа на отсутствие времени в запросе """
        del self.norm[TIME]
        self.assertEqual(process_client_message(self.norm), self.bad_request)


if __name__ == '__main__':
    unittest.main()