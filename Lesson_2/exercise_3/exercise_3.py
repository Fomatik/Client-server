"""
3. Задание на закрепление знаний по модулю yaml.
Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список,
второму — целое число, третьему — вложенный словарь,
где значение каждого ключа — это целое число с юникод-символом, отсутствующим в кодировке ASCII (например, €);

Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
При этом обеспечить стилизацию файла с помощью параметра default_flow_style,
а также установить возможность работы с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
"""
import yaml


def dict_in_yaml():
    data = {
        'list': ['лыжи', 'сноуборд', 48],
        'number': 23,
        'dict': {
            'one': '5 €',
            'two': '23 ₿',
            'three': '54 ₽'
        }
    }
    
    print(data)
    print(type(data))

    with open('file.yaml', 'w', encoding='utf-8') as f_n:
        yaml.dump(data, f_n, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # При чтении YAML файла данные не изменились.

    with open('file.yaml', encoding='utf-8') as f_n:
        content = yaml.load(f_n, Loader=yaml.FullLoader)
        print(content)
        print(type(content))
    
    
if __name__ == '__main__':
    dict_in_yaml()
