"""Константы"""

# Порт по умолчанию
SERVER_PORT = 7777
# IP-адрес сервера
SERVER_IP = '127.0.0.1'
# Максимальная очередь подключения
MAX_CONNECTIONS = 1
# Максимальная длинна сообщения (байты)
MAX_MSG_LEN = 1024
# Кодировка
ENCODING = 'utf-8'

# Ключи протокола JIM
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# Дополнительные ключи JIM
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
RESPONSE_DEFAULT_IP_ADDRESS = 'response_default_ip_address'