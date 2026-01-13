import base64


def convert_to_base64(text_to_encode):
    encoded_text = base64.b64encode(text_to_encode.encode()).decode()
    return encoded_text


def decode_base64(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_text = decoded_bytes.decode('utf-8')
    return decoded_text
