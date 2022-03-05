""" Основной файл работы сервера """

import argparse
import logging
import os
import sys
import threading
from select import select
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

sys.path.append(os.path.join(os.path.dirname(__file__), './common'))

from common.setting import SERVER_IP, SERVER_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, \
    ERROR, MESSAGE, SENDER, MESSAGE_TEXT, RESPONSE_200, RESPONSE_400, DESTINATION, EXIT
from common.utils import get_message, send_message
from common.decos import log
from common.descriptors import Port
from metaclasses import ServerVerifier
from server_bd import ServerDB

# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')


@log
def arg_parser():
    """
    Парсер аргументов командной строки.
    :return: ip, port
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=SERVER_IP, nargs='?', help=f'IP адрес для старта сервера (по умолчанию: '
                                                                 f'{SERVER_IP})')
    parser.add_argument('-p', default=SERVER_PORT, type=int, nargs='?', help=f'Порт для старта сервера 1024-65535 '
                                                                             f'(по умолчанию: {SERVER_PORT})')
    namespace = parser.parse_args(sys.argv[1:])
    ip = namespace.a
    port = namespace.p

    return ip, port


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listening_address, listening_port, database):
        # Сокет
        self.socket = socket(AF_INET, SOCK_STREAM)
        # Порт и адрес сервера
        self.ip = listening_address
        self.port = listening_port
        # База данных сервера
        self.database = database
        # Список клиентов, очередь сообщений
        self.clients = []
        self.messages = []
        # Словарь, содержащий имена пользователей и соответствующие им сокеты.
        self.names = dict()

        super().__init__()

    def __init_socket(self):
        try:
            # Настройки сокета
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            # IP и PORT
            self.socket.bind((self.ip, self.port))
            # Таймаут метода accept
            self.socket.settimeout(0.5)
            # Слушаем адрес сервера и задаём размер очереди
            self.socket.listen(MAX_CONNECTIONS)
        except OSError as e:
            SERVER_LOGGER.critical(e)
        else:
            SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {self.port}, '
                               f'адрес с которого принимаются подключения: {self.ip if self.ip else "ANY"}. '
                               f'Если адрес не указан, принимаются соединения с любых адресов.')
            print(f'Запущен сервер: {self.ip}:{self.port}.')

    def run(self):
        # Инициализация Сокета
        self.__init_socket()

        try:
            while True:
                try:
                    client, client_address = self.socket.accept()
                except OSError:
                    pass
                else:
                    SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
                    self.clients.append(client)

                recv_client_lst = []
                send_client_lst = []
                err_lst = []

                try:
                    if self.clients:
                        recv_client_lst, send_client_lst, err_lst = select(self.clients, self.clients, [], 0)
                except OSError:
                    pass

                # принимаем сообщения и если ошибка, исключаем клиента.
                if recv_client_lst:
                    for client_with_msg in recv_client_lst:
                        try:
                            self.process_client_message(get_message(client_with_msg), client_with_msg)
                        except Exception as e:
                            SERVER_LOGGER.info(f'Клиент {client_with_msg.getpeername()} отключился от сервера. {e}')
                            self.clients.remove(client_with_msg)

                # Если есть сообщения, обрабатываем каждое.
                for message in self.messages:
                    try:
                        self.process_message(message, send_client_lst)
                    except Exception:
                        SERVER_LOGGER.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
                        self.clients.remove(self.names[message[DESTINATION]])
                        del self.names[message[DESTINATION]]
                self.messages.clear()

        finally:
            self.socket.close()

    def process_message(self, message, listen_socks):
        """
            Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
            список зарегистрированных пользователей и слушающие сокеты. Ничего не возвращает.
            :param message:
            :param listen_socks:
            :return: None
            """
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            SERVER_LOGGER.info(
                f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            SERVER_LOGGER.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    def process_client_message(self, message, client):
        """Функция для формирования ответа клиенту
            :param message:
            :param client:
            :return: None
            """
        SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        try:
            if message.keys() >= {ACTION, TIME}:
                if message[ACTION] == PRESENCE and USER in message:
                    if message[USER][ACCOUNT_NAME] not in self.names.keys():
                        self.names[message[USER][ACCOUNT_NAME]] = client
                        print(self.names)
                        client_ip, client_port = client.getpeername()
                        self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                        send_message(client, RESPONSE_200)
                    else:
                        response = RESPONSE_400
                        response[ERROR] = 'Имя пользователя уже занято.'
                        send_message(client, response)
                        self.clients.remove(client)
                        client.close()
                    return
                # Если это сообщение, то добавляем его в очередь сообщений.
                elif message[ACTION] == MESSAGE and DESTINATION in message and \
                        SENDER in message and MESSAGE_TEXT in message:
                    self.messages.append(message)
                    return
                # Если клиент выходит
                elif message[ACTION] == EXIT and ACCOUNT_NAME in message:
                    self.database.user_logout(message[ACCOUNT_NAME])
                    self.clients.remove(self.names[message[ACCOUNT_NAME]])
                    self.names[message[ACCOUNT_NAME]].close()
                    print(self.names)
                    del self.names[message[ACCOUNT_NAME]]
                    print(self.names)
                    return
                else:
                    raise ValueError
            raise KeyError
        except (ValueError, KeyError):
            SERVER_LOGGER.error(f'Неправильное сообщение от клиента {client.getpeername()}: {message}')
            RESPONSE_400[ERROR] = 'Запрос некорректен.'
            send_message(client, RESPONSE_400)
            return


def print_help():
    print('Поддерживаемые команды:')
    print('users - список известных пользователей')
    print('connected - список подключённых пользователей')
    print('loglist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def main():
    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умолчанию.
    ip, port = arg_parser()

    # Инициализация базы данных
    database = ServerDB()

    # Создание экземпляра класса - сервера и его запуск:
    server = Server(ip, port, database)
    server.daemon = True
    server.start()

    # Печатаем справку:
    print_help()

    # Основной цикл сервера:
    while True:
        command = input('Введите команду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(database.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loglist':
            name = input('Введите имя пользователя для просмотра истории. '
                         'Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':

    SERVER_LOGGER.error('!!!')
    main()
