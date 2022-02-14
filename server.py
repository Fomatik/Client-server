"""
1. Реализовать простое клиент-серверное взаимодействие по протоколу JIM (JSON instant messaging):
клиент отправляет запрос серверу; сервер отвечает соответствующим кодом результата. Клиент и сервер должны быть
реализованы в виде отдельных скриптов, содержащих соответствующие функции.

Функции сервера: принимает сообщение клиента; формирует ответ клиенту; отправляет ответ клиенту;
имеет параметры командной строки: -p <port> — TCP-порт для работы (по умолчанию использует 7777);
-a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
"""
import argparse
import logging
import os
import sys
import time
from select import select

sys.path.append(os.path.join(os.path.dirname(__file__), './common'))

from common.setting import SERVER_IP, SERVER_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, \
    RESPONSE, ERROR, MESSAGE, SENDER, MESSAGE_TEXT, RESPONSE_200, RESPONSE_400, DESTINATION, EXIT
from common.utils import get_message, send_message
from common.decos import log
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message: dict, messages_list, client, clients, names) -> dict:
    """Функция для формирования ответа клиенту
    :param names:
    :param clients:
    :param message:
    :param messages_list:
    :param client:
    :return:
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    try:
        if message.keys() >= {ACTION, TIME}:
            if message[ACTION] == PRESENCE and USER in message:
                if message[USER][ACCOUNT_NAME] not in names.keys():
                    names[message[USER][ACCOUNT_NAME]] = client
                    send_message(client, RESPONSE_200)
                else:
                    response = RESPONSE_400
                    response[ERROR] = 'Имя пользователя уже занято.'
                    send_message(client, response)
                    clients.remove(client)
                    client.close()
                return
            # Если это сообщение, то добавляем его в очередь сообщений.
            elif message[ACTION] == MESSAGE and DESTINATION in message and SENDER in message and MESSAGE_TEXT in message:
                messages_list.append(message)
                return
            # Если клиент выходит
            elif message[ACTION] == EXIT and ACCOUNT_NAME in message:
                clients.remove(names[message[ACCOUNT_NAME]])
                names[message[ACCOUNT_NAME]].close()
                del names[message[ACCOUNT_NAME]]
                return
            else:
                raise ValueError
        raise KeyError
    except (ValueError, KeyError):
        SERVER_LOGGER.error(f'Неправильное сообщение от клиента {client.getpeername()}: {message}')
        RESPONSE_400[ERROR] = 'Запрос некорректен.'
        send_message(client, RESPONSE_400)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированных пользователей и слушающие сокеты. Ничего не возвращает.
    :param message:
    :param names:
    :param listen_socks:
    :return:
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


@log
def create_arg_parser():
    """
    Парсер аргументов коммандной строки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=SERVER_IP, nargs='?', help=f'IP адрес для старта сервера (по умолчанию: '
                                                                 f'{SERVER_IP})')
    parser.add_argument('-p', default=SERVER_PORT, type=int, nargs='?', help=f'Порт для старта сервера 1024-65535 (по умолчанию: {SERVER_PORT})')
    namespace = parser.parse_args(sys.argv[1:])
    listening_address = namespace.a
    listening_port = namespace.p

    # проверка получения корректного номера порта для работы сервера.
    if not 1023 < listening_port < 65536:
        SERVER_LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                               f'{listening_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listening_address, listening_port


def main():
    """
    Основная функция запуска сервера.
    Функция читает параметры командной строки; создаёт сокет согласно параметрам командной строки или с
    параметрами по умолчанию; открывает сокет для соединения с клиентами; получает PRESENCE сообщение от клиента и
    формирует ответ в виде кода; отправляет сообщение клиенту; закрывает соединение с клиентом.
    """

    # Получение номера порта из параметров командной строки
    listening_address, listening_port = create_arg_parser()

    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listening_port}, '
                       f'адрес с которого принимаются подключения: {listening_address}. '
                       f'Если адрес не указан, принимаются соединения с любых адресов.')

    # Сокет
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # IP и PORT
    serv_sock.bind((listening_address, listening_port))
    # Таймаут метода accept
    serv_sock.settimeout(0.5)
    # Слушаем адрес сервера и задаём размер очереди
    serv_sock.listen(MAX_CONNECTIONS)

    # список клиентов, очередь сообщений
    clients = []
    messages = []

    # Словарь, содержащий имена пользователей и соответствующие им сокеты.
    names = dict()  # {client_name: client_socket}

    # Открытие и закрытие соединения с клиентом
    # Получение и отправка сообщения клиенту
    try:
        while True:
            try:
                client, client_address = serv_sock.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
                clients.append(client)

            recv_client_lst = []
            send_client_lst = []
            err_lst = []

            try:
                if clients:
                    recv_client_lst, send_client_lst, err_lst = select(clients, clients, [], 0)
            except OSError:
                pass

            if recv_client_lst:
                for client_with_msg in recv_client_lst:
                    try:
                        process_client_message(get_message(client_with_msg), messages, client_with_msg, clients, names)
                    except Exception:
                        SERVER_LOGGER.info(f'Клиент {client_with_msg.getpeername()} отключился от сервера.')
                        clients.remove(client_with_msg)

            # Если есть сообщения, обрабатываем каждое.
            for i in messages:
                try:
                    process_message(i, names, send_client_lst)
                except Exception:
                    SERVER_LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
            messages.clear()

    finally:
        serv_sock.close()


if __name__ == '__main__':
    main()