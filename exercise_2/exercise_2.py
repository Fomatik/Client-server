"""
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
Написать скрипт, автоматизирующий его заполнение данными. Для этого:

Создать функцию write_order_to_json(), в которую передается 5 параметров —
товар (item), количество (quantity), цена (price), покупатель (buyer), дата (date).
В это словаре параметров обязательно должны присутствовать юникод-символы, отсутствующие в кодировке ASCII.

Функция должна предусматривать запись данных в виде словаря в файл orders.json.
При записи данных указать величину отступа в 4 пробельных символа;

Необходимо также установить возможность отображения символов юникода: ensure_ascii=False;

Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
"""
import json
from datetime import datetime


def write_order_to_json(item: str, quantity: int, price: float, buyer: str, date: str):
    order = {
        'товар': item,
        'количество': quantity,
        'цена': price,
        'покупатель': buyer,
        'дата': date,
    }

    with open('orders.json', 'r', encoding='utf-8') as of_r:
        order_f = json.load(of_r)

    with open('orders.json', 'w', encoding='utf-8') as of_w:
        order_f['orders'].append(order)
        json.dump(order_f, of_w, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    write_order_to_json('Кукуруза', 5, 5.55, 'Кукурузин', datetime.now().strftime('%H:%M:%S'))
    write_order_to_json('Картошка', 7, 7.00, 'Картошкин', datetime.now().strftime('%H:%M:%S'))
    write_order_to_json('Картошка', 7, 7.00, 'Картошкин', datetime.now().strftime('%H:%M:%S'))
    write_order_to_json('Картошка', 7, 7.00, 'Картошкин', datetime.now().strftime('%H:%M:%S'))
    write_order_to_json('Картошка', 7, 7.00, 'Картошкин', datetime.now().strftime('%H:%M:%S'))