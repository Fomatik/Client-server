"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только
последний октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.
"""
from exercise_1 import host_ping, check_address


def host_range_ping(get_dict=False):
    print('Программа сканирования ip адресов по последнему октету.\n')
    while True:
        start_ip = input('Введите стартовый ip адрес: ')
        try:
            start_ipv4 = check_address(start_ip)
            break
        except ValueError:
            print('Вы ввели не правильный ip адрес. Попробуйте ещё раз.')
    start_oct = int(start_ip.split('.')[3])
    while True:
        range_addr = int(input(f'Введите количество адресов для сканирования ({start_ip} + n): '))
        if start_oct + range_addr > 255:
            print(f'Можем менять только последний октет, т.е. максимальное число хостов {255 - start_oct}')
        else:
            break
    addr_list = [str(start_ipv4 + n) for n in range(range_addr)]

    if not get_dict:
        return host_ping(addr_list)
    else:
        return host_ping(addr_list, get_dict=True)


if __name__ == '__main__':
    host_range_ping()
