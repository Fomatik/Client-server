import json

from setting import MAX_MSG_LEN, ENCODING


def get_message(client):
    """
    Функция получения, декодирования и десериализации JIM сообщения в obj.
    """
    encode_msg = client.recv(MAX_MSG_LEN)
    if isinstance(encode_msg, bytes):
        decode_msg = encode_msg.decode(ENCODING)
        json_from_msg = json.loads(decode_msg)
        if isinstance(json_from_msg, dict):
            return json_from_msg
        raise ValueError
    raise ValueError


def send_message(socket, message):
    """
    Функция сериализации obj в JIM, кодирования и отправки сообщения.
    """
    if not isinstance(message, dict):
        raise TypeError

    json_message = json.dumps(message)
    encoded_msg = json_message.encode('utf-8')
    socket.send(encoded_msg)
