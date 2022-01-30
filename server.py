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
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'log'))

from common.setting import SERVER_IP, SERVER_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, \
    RESPONSE, ERROR
from common.utils import get_message, send_message
from common.errors import IncorrectDataRecivedError
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import log.server_log_config

# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')


def process_client_message(message: dict) -> dict:
    """Функция для формирования ответа клиенту
    :param message:
    :return:
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    try:
        if message.keys() == {ACTION, TIME, USER}:
            if message[ACTION] == PRESENCE and message[USER][ACCOUNT_NAME] == 'Guest':
                return {RESPONSE: 200}
            else:
                raise ValueError
        raise KeyError
    except (ValueError, KeyError):
        SERVER_LOGGER.error(f'Неправильное PRESENCE сообщение от клиента: {message}')
        return {
            RESPONSE: 400,
            ERROR: 'BadRequest'
        }


def create_arg_parser():
    """
    Парсер аргументов коммандной строки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=SERVER_IP, nargs='?', help=f'IP адрес для старта сервера (по умолчанию: '
                                                                 f'{SERVER_IP})')
    parser.add_argument('-p', default=SERVER_PORT, type=int, nargs='?', help=f'Порт для старта сервера 1024-65535 (по умолчанию: {SERVER_PORT})')

    return parser


def main():
    """
    Основная функция запуска сервера.
    Функция читает параметры командной строки; создаёт сокет согласно параметрам командной строки или с
    параметрами по умолчанию; открывает сокет для соединения с клиентами; получает PRESENCE сообщение от клиента и
    формирует ответ в виде кода; отправляет сообщение клиенту; закрывает соединение с клиентом.
    """

    # Получение номера порта из параметров командной строки
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listening_address = namespace.a
    listening_port = namespace.p

    # проверка получения корректного номера порта для работы сервера.
    if not 1023 < listening_port < 65536:
        SERVER_LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                               f'{listening_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)
    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listening_port}, '
                       f'адрес с которого принимаются подключения: {listening_address}. '
                       f'Если адрес не указан, принимаются соединения с любых адресов.')

    # Сокет
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # IP и PORT
    serv_sock.bind((listening_address, listening_port))
    # Слушаем адрес сервера и задаём размер очереди
    serv_sock.listen(MAX_CONNECTIONS)

    # Открытие и закрытие соединения с клиентом
    # Получение и отправка сообщения клиенту
    try:
        while True:
            client, client_address = serv_sock.accept()
            SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
            try:
                msg_from_client = get_message(client)
                SERVER_LOGGER.debug(f'Получено сообщение {msg_from_client}')
                response_msg = process_client_message(msg_from_client)
                SERVER_LOGGER.info(f'Сформирован ответ клиенту {response_msg}')
                send_message(client, response_msg)
                SERVER_LOGGER.debug(f'Соединение с клиентом {client_address} закрывается.')
                client.close()
            except json.JSONDecodeError:
                SERVER_LOGGER.error(f'Не удалось декодировать Json строку, полученную от клиента {client_address}. '
                                    f'Соединение закрывается.')
                client.close()
            except IncorrectDataRecivedError:
                SERVER_LOGGER.error(f'От клиента {client_address} приняты некорректные данные. '
                                    f'Соединение закрывается.')
                client.close()
    finally:
        serv_sock.close()


if __name__ == '__main__':
    main()