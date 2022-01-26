"""
1. Реализовать простое клиент-серверное взаимодействие по протоколу JIM (JSON instant messaging):
клиент отправляет запрос серверу; сервер отвечает соответствующим кодом результата. Клиент и сервер должны быть
реализованы в виде отдельных скриптов, содержащих соответствующие функции.

Функции сервера: принимает сообщение клиента; формирует ответ клиенту; отправляет ответ клиенту;
имеет параметры командной строки: -p <port> — TCP-порт для работы (по умолчанию использует 7777);
-a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
"""
import sys
import json

from common.setting import SERVER_IP, SERVER_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, \
    RESPONSE, ERROR
from common.utils import get_message, send_message
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR


def process_client_message(message: dict) -> dict:
    """Функция для формирования ответа клиенту
    :param message:
    :return:
    """
    try:
        if message.keys() == {ACTION, TIME, USER}:
            if message[ACTION] == PRESENCE and message[USER][ACCOUNT_NAME] == 'Guest':
                return {RESPONSE: 200}
            else:
                raise ValueError
        raise KeyError
    except (ValueError, KeyError):
        return {
            RESPONSE: 400,
            ERROR: 'BadRequest'
        }


def main():
    """
    Основная функция запуска сервера.
    Функция читает параметры командной строки; создаёт сокет согласно параметрам командной строки или с
    параметрами по умолчанию; открывает сокет для соединения с клиентами; получает PRESENCE сообщение от клиента и
    формирует ответ в виде кода; отправляет сообщение клиенту; закрывает соединение с клиентом.
    """

    # Получение номера порта из параметров командной строки
    try:
        if '-p' in sys.argv:
            listening_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listening_port = SERVER_PORT
        if listening_port < 1024 and listening_port < 65535:
            raise ValueError
    except (IndexError, ValueError):
        print('Необходимо указать номер порта \'-p (1024-65535)\'!')
        sys.exit(1)

    # Получение ip адреса из параметров командной строки
    try:
        if '-a' in sys.argv:
            listening_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listening_address = SERVER_IP
    except IndexError:
        print('Необходимо указать ip-адрес \'-a (IPv4)\'!')
        sys.exit(1)

    print(f'Порт: {listening_port}')
    print(f'IP: {listening_address}')

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
            try:
                msg_from_client = get_message(client)
                print(f'Сообщение от клиента: {msg_from_client}')
                response_msg = process_client_message(msg_from_client)
                print(f'Ответ клиенту: {response_msg}')
                send_message(client, response_msg)
                client.close()
            except json.JSONDecodeError:
                client.close()
    finally:
        serv_sock.close()


if __name__ == '__main__':
    main()