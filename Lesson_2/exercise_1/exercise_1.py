"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из
файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание
данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и
поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта»,
«Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для
каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение
данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;

Проверить работу программы через вызов функции write_to_csv().
"""
import csv
import re
from chardet import detect


list_files = ['info_1.txt', 'info_2.txt', 'info_3.txt']


def get_data(files: list):
    main_data = []
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []

    for file in files:
        with open(file, 'rb') as encode_file:
            content = encode_file.read()
            content = content.decode(detect(content)['encoding']).split('\n')

            for line in content:
                line = ' '.join(line.split())
                os_prod = re.match(r"^Изготовитель системы.*$", line)
                if os_prod:
                    os_prod = os_prod.group(0).split(r': ')
                    os_prod_list.append(os_prod[1])
                os_name = re.match(r'^Название ОС.*$', line)
                if os_name:
                    os_name = os_name.group(0).split(r': ')
                    os_name_list.append(os_name[1])
                os_code = re.match(r'^Код продукта.*$', line)
                if os_code:
                    os_code = os_code.group(0).split(r': ')
                    os_code_list.append(os_code[1])
                os_type = re.match(r'^Тип системы.*$', line)
                if os_type:
                    os_type = os_type.group(0).split(r': ')
                    os_type_list.append(os_type[1])

    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.append(headers)

    for i in range(len(os_prod_list)):
        values_list = []
        values_list.append(os_prod_list[i])
        values_list.append(os_name_list[i])
        values_list.append(os_code_list[i])
        values_list.append(os_type_list[i])
        main_data.append(values_list)

    return main_data


def write_to_csv():
    data = get_data(list_files)
    with open('main_data.csv', 'w', encoding='utf-8', newline='') as f_n:
        f_n_writer = csv.writer(f_n)
        f_n_writer.writerows(data)


if __name__ == '__main__':
    write_to_csv()
