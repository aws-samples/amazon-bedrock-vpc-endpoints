import base64

def encode_string_to_base64(text):
    #Encodes a string to base64
    return base64.b64encode(text).decode('utf-8')

def decode_base64_to_string(text):
    #Decodes a base64 string to a string
    return base64.b64decode(text).decode('utf-8')