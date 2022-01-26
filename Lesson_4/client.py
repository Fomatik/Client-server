"""
Функции клиента: сформировать presence-сообщение; отправить сообщение серверу;
получить ответ сервера; разобрать сообщение сервера; параметры командной строки скрипта client.py <addr> [<port>]:
addr — ip-адрес сервера; port — tcp-порт на сервере, по умолчанию 7777.
"""

import json
import sys
import time

from common.utils import send_message, get_message
from common.setting import SERVER_PORT, SERVER_IP, ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, PRESENCE
from socket import socket, AF_INET, SOCK_STREAM


def create_presence(account_name: str = 'Guest') -> dict:
    """
    Функция формирования PRESENCE сообщения
    :param account_name:
    :return:
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return out


def process_answer(message: dict) -> str:
    """
    Функция обработки ответа сервера
    :param message:
    :return:
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    raise ValueError


def main():
    """
    Основная функция клиента.
    Функция читает параметры командной строки для соединения с сервером; открывает соединение с сервером; отправляет
    PRESENCE сообщение; обрабатывает ответ сервера.
    """
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = SERVER_IP
    if len(sys.argv) > 2:
        server_port = int(sys.argv[2][1:-1])
    else:
        server_port = SERVER_PORT

    client_sock = socket(AF_INET, SOCK_STREAM)
    client_sock.connect((server_ip, server_port))
    msg = create_presence()
    send_message(client_sock, msg)
    try:
        answer = process_answer(get_message(client_sock))
        print(answer)
    except json.JSONDecodeError:
        print('Не правильный ответ от сервера.')


if __name__ == '__main__':
    main()
