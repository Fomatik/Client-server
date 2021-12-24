# 1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и содержание
# соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые представление в формат Unicode
# и также проверить тип и содержимое переменных.

str_var = ['разработка', 'сокет', 'декоратор']
unicode_var = ['\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
               '\u0441\u043e\u043a\u0435\u0442',
               '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
               ]


def var_type(words: list):
    for word in words:
        print(f'Значение переменной: {word}, \nТип переменной: {type(word)}')
        print('-' * 100)


var_type(str_var)
var_type(unicode_var)

