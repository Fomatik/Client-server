# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет»,
# «декоратор». Проверить кодировку созданного файла (исходить из того, что вам априори неизвестна кодировка этого
# файла!). Затем открыть этот файл и вывести его содержимое на печать. ВАЖНО: файл должен быть открыт без ошибок вне
# зависимости от того, в какой кодировке он был создан!
from chardet import detect

# file = 'test_file.txt'
#
# encoding = detect(file)['encoding']
# print(encoding)


def read_encoding_file(reading_file: str):
    with open(reading_file, 'rb') as file:
        content = file.read()

    encoding = detect(content)['encoding']
    print(f'Кодировка файла: {encoding}\n')

    with open(reading_file, 'r', encoding=encoding) as file:
        print('Содержание файла: \n')
        for string in file:
            print(string, end='')


read_encoding_file('test_file.txt')