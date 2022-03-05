import logging

SERVER_LOGGER = logging.getLogger('server')


# Дескриптор для описания порта:
class Port:
    """ Дескриптор для описания порта: """
    def __set__(self, instance, value):
        """
        Метод дескриптора для проверки порта сервера (1024-65536)
        :param instance:
        :param value:
        """

        if not (1023 < value < 65536) and not (isinstance(value, int)):
            SERVER_LOGGER.critical(
                f'Попытка запуска сервера с неподходящим портом {value}. Допустимый порт с 1024 до 65535.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        """
        :param owner:
        :param name:
        """

        self.name = name

