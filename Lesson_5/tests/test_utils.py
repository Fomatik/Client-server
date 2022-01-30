"""
Unittest для функций utils
"""
import json
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../common'))

from common.setting import ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR, ENCODING
from common.utils import get_message, send_message
from common.errors import NonDictInputError


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message):
        """

        :param message:
        :return:
        """
        json_from_message = json.dumps(self.test_dict)
        self.encoded_message = json_from_message.encode(ENCODING)
        self.received_message = message

    def recv(self, max_len):
        """

        :param max_len:
        :return:
        """
        json_message = json.dumps(self.test_dict)
        return json_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    test_dict = {
        ACTION: PRESENCE,
        TIME: 1.1,
        USER: {
            ACCOUNT_NAME: 'Guest'
        }
    }

    test_recv = {RESPONSE: 200}

    test_error_recv = {
        RESPONSE: 400,
        ERROR: 'BadRequest'
    }

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_send_wrong_message_from_client(self):
        self.assertRaises(NonDictInputError, send_message, TestSocket(self.test_dict), 'message')

    def test_send_message_from_client_to_server(self):
        test_socket = TestSocket(self.test_dict)
        send_message(test_socket, self.test_dict)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

    def test_get_ok_msg(self):
        test_sock_ok = TestSocket(self.test_recv)
        self.assertEqual(get_message(test_sock_ok), self.test_recv)

    def test_get_err_msg(self):
        test_sock_error = TestSocket(self.test_error_recv)
        self.assertEqual(get_message(test_sock_error), self.test_error_recv)


if __name__ == '__main__':
    unittest.main()
