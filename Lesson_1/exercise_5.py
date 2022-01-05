# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтового в строковый
# (предварительно определив кодировку выводимых сообщений).

import chardet
import subprocess
import platform

list_site = ['yandex.ru', 'youtube.com']


def ping(sites: list):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    for ping_site in sites:
        args = ['ping', param, '2', ping_site]
        result = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in result.stdout:
            result = chardet.detect(line)
            line = line.decode(result['encoding']).encode('utf-8')
            print(line.decode('utf-8'))

        print('-' * 100)
        
        
ping(list_site)
