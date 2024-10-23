import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from email.utils import parseaddr
from config import Config
import base64


class Privacy:
    def __init__(self, key=None, iv=None):
        self.key = self.__handle_key(key)
        self.iv = self.__handle_iv(iv)
        self.backend = default_backend()

    def __handle_key(self, key):
        base64_key = Config.PRIVACY_KEY if key is None else key
        padding_length = 4 - (len(base64_key) % 4)
        base64_key += "=" * padding_length
        key_bytes = base64.b64decode(base64_key)
        key_size = len(key_bytes)
        if key is not None:
            key_bytes = key

        if key_size not in (16, 24, 32):
            raise ValueError("Invalid key size ({}) for AES".format(key_size))
        return key_bytes

    def __handle_iv(self, iv):
        if iv is None:
            ivlen = algorithms.AES.block_size // 8
            return os.urandom(ivlen)
        else:
            return base64.b64decode(iv)

    def encrypt(self, plaintext):
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=self.backend)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()

        plaintext_bytes = plaintext.encode()
        padded_plaintext = padder.update(plaintext_bytes) + padder.finalize()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return base64.b64encode(ciphertext).decode('utf-8') + '|||' + base64.b64encode(self.iv).decode('utf-8')

    def decrypt(self, ciphertext):
        ciphertext, iv = ciphertext.split('|||')
        self.iv = base64.b64decode(iv)
        ciphertext = base64.b64decode(ciphertext)

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=self.backend)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        decrypted_padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        return plaintext.decode('utf-8')

    @staticmethod
    def mask_ip(ip):
        components = ip.split(".")
        masked_ip = ".".join(components[:-1]) + ".0"
        return masked_ip

    def secure_email(self, email_string, return_raw=False):
        email = email_string.lower().strip()
        out = {
            'error': 'true',
            'email_valid': 'yes',
            'email_normalized': email
        }

        # Validates the format of the email
        _, email_address = parseaddr(email)
        if not email_address:
            reason = 'Invalid Email Format. '
            out['email_valid'] = 'no'
            out['reason'] = reason
            return out

        # Validates the email is not a 'default sample' like my@email.com
        if email.endswith('@email.'):
            reason = 'Generic Email Format. '
            out['email_valid'] = 'no'
            out['reason'] = reason
            return out

        out['error'] = 'false'
        em = email.split('@')
        name = '@'.join(em[:-1])
        length = min(len(name) // 2, 3)
        domain = em[-1]

        # standard output for a secure field method
        hash_algorithm = hashlib.sha256()  # or hashlib.sha512() for a stronger hash
        hash_algorithm.update(email.encode())
        out['hash'] = hash_algorithm.hexdigest()
        out['mask'] = name[:length] + '*' * 5 + name[-1] + '@' + domain
        out['domain'] = domain
        out['encrypted'] = self.encrypt(email)
        if return_raw:
            out['raw'] = email

        return out

    @staticmethod
    def mask_phone_number(phone_number, mask_char='*', num_visible_digits=4):
        visible_digits = phone_number[-num_visible_digits:]
        masked_digits = mask_char * (len(phone_number) - num_visible_digits)
        return masked_digits + visible_digits

    @staticmethod
    def hash_string(string):
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(string.encode())
        return hash_algorithm.hexdigest()
