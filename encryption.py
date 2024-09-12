from cryptography.fernet import Fernet
import logging
from logging_setup import setup_logging

# Set up logging using the imported function
setup_logging(log_level=logging.INFO)

def generateKey():
    # generate secret key to use for encryption
    key = Fernet.generate_key()
    #print('key: ', key)
    return key

def encrypt(key, data):
    f = Fernet(key)
     # convert string to bytes
    encoded = str.encode(data)
    # use Fernet to encrypt using Symmetric encryption
    encrypted = f.encrypt(encoded)
    #print(encrypted)
    return encrypted

def decrypt(key, encrypted):
     # convert string to bytes
    encoded = str.encode(encrypted)
    f = Fernet(key)
    # use Fernet to decrypt using Symmetric encryption
    decrypted = f.decrypt(encoded)
    # convert bytes to string
    decoded = decrypted.decode()
    #print(decoded)
    return decoded

logging.info(f"generateKey().decode() is {generateKey().decode()}")    
#print(generateKey().decode())

#if __name__ == '__main__':
    # converting bytes to string
    #print(generateKey().decode())
