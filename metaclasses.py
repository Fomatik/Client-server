""" Метакласс для проверки соответствия сервера и проверки корректности клиентов"""

import dis


# Метакласс для проверки соответствия сервера
class ServerVerifier(type):
    def __init__(cls, name, bases, dct):
        """
        :param name:
        :param bases:
        :param dct:
        """
        # Список методов, которые используются в функциях класса:
        methods = []
        # Атрибуты, используемые в функциях классов
        attrs = []

        for func in dct:
            try:
                ret = dis.get_instructions(dct[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # заполняем список методами, использующимися в функциях класса
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)

        # Если обнаружено использование недопустимого метода connect, вызываем исключение:
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')

        # Если сокет не инициализировался константами SOCK_STREAM(TCP) AF_INET(IPv4), тоже исключение.
        # Т.к. AF_INET и SOCK_STREAM загружены глобально, а не как аттрибуты, ищем их в methods
        if not ('SOCK_STREAM' in methods and 'AF_INET' in methods):
            raise TypeError('Некорректная инициализация сокета.')

        super().__init__(name, bases, dct)


# Метакласс для проверки корректности клиентов:
class ClientVerifier(type):
    def __init__(cls, name, bases, dct):
        # Список методов, которые используются в функциях класса:
        methods = []
        attrs = []

        for func in dct:
            try:
                ret = dis.get_instructions(dct[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)
        print(methods)
        print(attrs)

        # Если обнаружено использование недопустимого метода accept, listen, socket бросаем исключение:
        for command in ('accept', 'listen'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')

        # Вызов get_message или send_message из utils считаем корректным использованием сокетов
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')

        super().__init__(name, bases, dct)