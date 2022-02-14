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
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), './common'))

from common.errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from common.utils import send_message, get_message
from common.setting import SERVER_PORT, SERVER_IP, ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, PRESENCE, \
    MESSAGE_TEXT, MESSAGE, SENDER, DESTINATION, EXIT
from common.decos import log
from socket import socket, AF_INET, SOCK_STREAM

# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')


@log
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def message_from_server(sock, my_username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной команды
    """
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except Exception as e:
        print(e)
        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@log
def user_interactive(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            # Задержка необходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробуйте снова. help - вывести поддерживаемые команды.')


@log
def create_presence(account_name: str) -> dict:
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
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


def print_help():
    """Функция выводящая справку по использованию"""
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


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
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
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
    parser.add_argument('-n', '--name', default=None, nargs='?', help='Имя пользователя')

    namespace = parser.parse_args(sys.argv[1:])
    server_ip = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
            f' Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_ip, server_port, client_name


def main():
    """
    Основная функция клиента.
    Функция читает параметры командной строки для соединения с сервером; открывает соединение с сервером; отправляет
    PRESENCE сообщение; обрабатывает ответ сервера.
    """
    server_ip, server_port, client_name = create_arg_parser()

    print(f'Консольный мессенджер. Клиентский модуль. Имя пользователя: {client_name}')

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    CLIENT_LOGGER.info(f'Запущен клиент с параметрами: адрес сервера: {server_ip} , порт: {server_port}, имя пользователя: {client_name}')

    try:
        client_sock = socket(AF_INET, SOCK_STREAM)
        client_sock.connect((server_ip, server_port))
        send_message(client_sock, create_presence(client_name))
        answer = process_answer(get_message(client_sock))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ConnectionError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_ip}:{server_port}, конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)

    else:
        # Если соединение с сервером установлено корректно,
        # запускаем клиентский процесс приёма сообщений
        receiver = threading.Thread(target=message_from_server, args=(client_sock, client_name))
        receiver.daemon = True
        receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_interface = threading.Thread(target=user_interactive, args=(client_sock, client_name))
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOGGER.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обрабатываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
