"""Константы"""

import logging

# Порт по умолчанию
SERVER_PORT = 7777
# IP-адрес сервера
SERVER_IP = '127.0.0.1'
# Максимальная очередь подключения
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения (байты)
MAX_MSG_LEN = 1024
# Кодировка
ENCODING = 'utf-8'
# Уровень логов по умолчанию
LOG_LVL = logging.DEBUG

# Ключи протокола JIM
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'

# Дополнительные ключи JIM
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'