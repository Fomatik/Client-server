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

from common.errors import ReqFieldMissingError, ServerError
from common.utils import send_message, get_message
from common.setting import SERVER_PORT, SERVER_IP, ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, PRESENCE, \
    MESSAGE_TEXT, MESSAGE, SENDER
from common.decos import log
from socket import socket, AF_INET, SOCK_STREAM

# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')


@log
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной команды
    """
    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


@log
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


@log
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


@log
def create_arg_parser():
    """
    Создаём парсер аргументов командной строки.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-addr', default=SERVER_IP, nargs='?', help='IP адрес сервера (по умолчанию: 127.0.0.1)')
    parser.add_argument('-port', default=SERVER_PORT, type=int, nargs='?', help='Порт сервера 1024-65535 (по умолчанию: 7777)')
    parser.add_argument('-m', '--mode', default='send', nargs='?', help='Режимы клиента listen или send')

    namespace = parser.parse_args(sys.argv[1:])
    server_ip = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
            f' Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, допустимые режимы: listen , send')
        sys.exit(1)

    return server_ip, server_port, client_mode


def main():
    """
    Основная функция клиента.
    Функция читает параметры командной строки для соединения с сервером; открывает соединение с сервером; отправляет
    PRESENCE сообщение; обрабатывает ответ сервера.
    """
    server_ip, server_port, client_mode = create_arg_parser()

    CLIENT_LOGGER.info(f'Запущен клиент с параметрами: адрес сервера: {server_ip} , порт: {server_port}, режим работы: {client_mode}')

    try:
        client_sock = socket(AF_INET, SOCK_STREAM)
        client_sock.connect((server_ip, server_port))
        send_message(client_sock, create_presence())
        answer = process_answer(get_message(client_sock))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_ip}:{server_port}, конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)

    else:
        # Если соединение с сервером установлено корректно,
        # начинаем обмен с ним, согласно требуемому режиму.
        # основной цикл прогрммы:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            # режим работы - отправка сообщений
            if client_mode == 'send':
                try:
                    send_message(client_sock, create_message(client_sock))
                except ConnectionError:
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_ip} было потеряно.')
                    sys.exit(1)

            # Режим работы приём:
            if client_mode == 'listen':
                try:
                    message_from_server(get_message(client_sock))
                except ConnectionError:
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_ip} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
