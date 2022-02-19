"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или
ip-адресом. В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего
сообщения («Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""
import locale
from socket import gethostbyname
import re
import platform
from ipaddress import ip_address, IPv4Address
from subprocess import Popen, PIPE
from threading import Thread


host_dict = {'Доступные хосты': [], 'Недоступные хосты': []}


def check_address(address: str):
    """
    Проверка является ли значение адресом хоста
    :param address:
    :return:
    """
    try:
        regex = re.compile(r"^(?:2[0-4][0-9]|25[0-5]|1?[0-9]?[0-9])[.](?:2[0-4][0-9]|25[0-5]|1?[0-9]?[0-9])[.](?:2["
                           r"0-4][0-9]|25[0-5]|1?[0-9]?[0-9])[.](?:2[0-4][0-9]|25[0-5]|1?[0-9]?[0-9])$")
        result = regex.match(address)
        if not result:
            try:
                address = gethostbyname(address)
            except OSError:
                raise ValueError
        else:
            address = result.group(0)
    finally:
        ipv4 = ip_address(address)
    return ipv4


def ping(address: str, host_ip_address, host_dict, get_dict):
    """
    Пинг
    :param get_dict:
    :param host_dict:
    :param address:
    :param host_ip_address:
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', param, '2', str(host_ip_address)]
    reply = Popen(args, stdout=PIPE, stderr=PIPE).communicate()[0]

    # Была проблема с поиском недоступных хостов в моей локальной сети в Windows
    # reply.wait() == 0 не срабатывал, т.к. ping проходил без ошибок
    # думаю такой поиск недоступных хостов будет работать на всех ОС и IP (и на локальных тоже)

    if any(x in reply for x in (b'unreachable', b'failed', b'Request timed out', b'100%')):
        ping_res = f'{address} -> Узел недоступен'
        host_dict['Недоступные хосты'].append(address)
    else:
        ping_res = f'{address} -> Узел доступен'
        host_dict['Доступные хосты'].append(address)

    if not get_dict:
        print(ping_res)
    else:
        return host_dict


def host_ping(address_lst: list, get_dict=False):
    """
    Запуск пинга каждого хоста в address_lst в отдельном потоке
    :param get_dict:
    :param address_lst:
    """
    print("Начинаю проверку доступности хостов...")
    threads = []
    for host_address in address_lst:
        try:
            host_ip_address = check_address(host_address)
        except ValueError:
            print(f'Значение "{host_address}" не является адресом хоста')
            continue
        thread = Thread(target=ping, args=(host_address, host_ip_address, host_dict, get_dict), daemon=True)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

    if get_dict:
        return host_dict


if __name__ == '__main__':
    hosts_list = ['192.168.100.30', '8.8.8.8', '0.0.0,0', 'yandex.ru', 'google.com', '0.0.0.1', '0.0.0.2', '0.0.0.3',
                  '0.0.0.4', '0.0.0.5', '0.0.0.6', '0.0.0.7', '0.0.0.8', '0.0.0.9', '0.0.1.0', 'f,dsdf']
    host_ping(hosts_list)
    # ping('192.168.100.30', check_address('192.168.100.30'))

