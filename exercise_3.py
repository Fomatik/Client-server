# 3. Определить, какие из слов, поданных на вход программы, невозможно записать в байтовом типе. Для проверки
# правильности работы кода используйте значения: «attribute», «класс», «функция», «type»

var = ['attribute', 'класс', 'функция', 'type']


def try_in_byte(words: list):
    for word in words:
        try:
            byte_word = eval(f"b'{word}'")
            print(f'"{word}" = {byte_word}')
        except SyntaxError:
            print(f'"{word}" = ошибка')
        print('-' * 50)


try_in_byte(var)
