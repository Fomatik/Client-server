# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в
# байтовое и выполнить обратное преобразование (используя методы encode и decode).

var = ['разработка', 'администрирование', 'protocol', 'standard']


def encode_decode(words: list):
    for word in words:
        byte_word = word.encode('utf-8')
        str_word = byte_word.decode('utf-8')
        print(f'Байтовое представление "{word}": {byte_word}')
        print(f'Строковое представление "{byte_word}": {str_word}')
        print('-' * 100)


encode_decode(var)
