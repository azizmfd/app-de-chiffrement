
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def aes_gcm_encrypt(input_path, output_path, key):
    key = key[:32].ljust(32, b'\0')
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    with open(input_path, 'rb') as f:
        data = f.read()

    ciphertext = aesgcm.encrypt(nonce, data, None)

    with open(output_path, 'wb') as f:
        f.write(nonce + ciphertext)

def aes_gcm_decrypt(input_path, output_path, key):
    key = key[:32].ljust(32, b'\0')

    with open(input_path, 'rb') as f:
        data = f.read()

    nonce = data[:12]
    ciphertext = data[12:]

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    with open(output_path, 'wb') as f:
        f.write(plaintext)


def aes_gcm_decrypt(input_path, output_path, key):
    key = key[:32].ljust(32, b'\0')

    with open(input_path, 'rb') as f:
        data = f.read()

    nonce = data[:12]
    ciphertext = data[12:]

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    with open(output_path, 'wb') as f:
        f.write(plaintext)
