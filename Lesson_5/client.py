"""
Функции клиента: сформировать presence-сообщение; отправить сообщение серверу;
получить ответ сервера; разобрать сообщение сервера; параметры командной строки скрипта client.py <addr> [<port>]:
addr — ip-адрес сервера; port — tcp-порт на сервере, по умолчанию 7777.
"""
import argparse
import json
import logging
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), './common'))
sys.path.append(os.path.join(os.path.dirname(__file__), './log'))

from common.errors import ReqFieldMissingError
from common.utils import send_message, get_message
from common.setting import SERVER_PORT, SERVER_IP, ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, PRESENCE
from socket import socket, AF_INET, SOCK_STREAM
import log.client_log_config

# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')


def create_presence(account_name: str = 'Guest') -> dict:
    """
    Функция формирования PRESENCE сообщения
    :param account_name: Guest
    :return:
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


def process_answer(message: dict) -> str:
    """
    Функция обработки ответа сервера
    :param message:
    :return:
    """
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


def create_arg_parser():
    """
    Создаём парсер аргументов командной строки.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-addr', default=SERVER_IP, nargs='?', help='IP адрес сервера (по умолчанию: 127.0.0.1)')
    parser.add_argument('-port', default=SERVER_PORT, type=int, nargs='?', help='Порт сервера 1024-65535 (по '
                                                                                'умолчанию: 7777)')
    return parser


def main():
    """
    Основная функция клиента.
    Функция читает параметры командной строки для соединения с сервером; открывает соединение с сервером; отправляет
    PRESENCE сообщение; обрабатывает ответ сервера.
    """
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_ip = namespace.addr
    server_port = namespace.port

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
            f' Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    CLIENT_LOGGER.info(f'Запущен клиент с параметрами: '
                       f'адрес сервера: {server_ip} , порт: {server_port}')

    try:
        client_sock = socket(AF_INET, SOCK_STREAM)
        client_sock.connect((server_ip, server_port))
        msg = create_presence()
        send_message(client_sock, msg)
        answer = process_answer(get_message(client_sock))
        CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
        print(answer)
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_ip}:{server_port}, '
                               f'конечный компьютер отверг запрос на подключение.')
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                            f'{missing_error.missing_field}')


if __name__ == '__main__':
    main()
