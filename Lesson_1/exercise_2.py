# 2. Каждое из слов «class», «function», «method» записать в байтовом типе. Сделать это необходимо в автоматическом,
# а не ручном режиме с помощью добавления литеры b к текстовому значению, (т.е. ни в коем случае не используя методы
# encode и decode) и определить тип, содержимое и длину соответствующих переменных.

str_word = ['class', 'function', 'method']


def byte_str(words: list):
    for word in words:
        byte_word = eval(f"b'{word}'")
        print(byte_word)
        print(type(byte_word))
        print(len(byte_word))
        print('-' * 20)


byte_str(str_word)
