""" Основной файл работы клиента """

import argparse
import json
import logging
import os
import sys
import time
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), './common'))

from socket import socket, AF_INET, SOCK_STREAM
from common.errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from common.utils import send_message, get_message
from common.setting import SERVER_PORT, SERVER_IP, ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, PRESENCE, \
    MESSAGE_TEXT, MESSAGE, SENDER, DESTINATION, EXIT
from common.decos import log
from metaclasses import ClientVerifier

# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')


@log
def arg_parser():
    """ Создаём парсер аргументов командной строки. """
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


# Класс формировки и отправки сообщений на сервер и взаимодействия с пользователем.
class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, client_name, sock):
        self.username = client_name
        self.sock = sock
        super().__init__()

    def create_exit_message(self):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }

    def create_message(self):
        """Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной команды
        """
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
        except Exception as e:
            print(e)
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            exit(1)

    def run(self):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                print('Завершение соединения.')
                CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
                # Задержка необходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробуйте снова. help - вывести поддерживаемые команды.')

    def print_help(self):
        """Функция выводящая справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


# Класс-приёмник сообщений с сервера. Принимает сообщения, выводит в консоль.
class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, client_name, sock):
        self.client_name = client_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.client_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    CLIENT_LOGGER.info(
                        f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                break


@log
def create_presence(client_name):
    """
    Функция формирования PRESENCE сообщения
    :param client_name:
    :return:
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: client_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {client_name}')
    return out


@log
def process_answer(message):
    """ Функция обработки ответа сервера """
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


def main():
    # Сообщаем о запуске
    print('Консольный мессенджер. Клиентский модуль.')

    # Загружаем параметры командной строки
    server_address, server_port, client_name = arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    CLIENT_LOGGER.info(
        f'Запущен клиент с парамерами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        client_sock = socket(AF_INET, SOCK_STREAM)
        client_sock.connect((server_address, server_port))
        send_message(client_sock, create_presence(client_name))
        answer = process_answer(get_message(client_sock))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:
        # Если соединение с сервером установлено корректно, запускаем клиентский процесс приёма сообщений
        module_receiver = ClientReader(client_name, client_sock)
        module_receiver.daemon = True
        module_receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        module_sender = ClientSender(client_name, client_sock)
        module_sender.daemon = True
        module_sender.start()

        CLIENT_LOGGER.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён, то значит потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обрабатываются в потоках, достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
