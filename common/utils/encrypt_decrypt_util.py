from django.conf import settings

from cryptography.fernet import Fernet


class MyFernet:
    def __init__(self):
        self.f_object = Fernet(bytes(settings.PRIVATE_KEY_ENCRYPT_DECRYPT, 'utf-8'))

    def encrypt_data(self, data):
        if data is None:
            return None
        return self.f_object.encrypt(data.encode('utf-8')).decode()

    def decrypt_data(self, data):
        data_modify = bytes(data, 'utf-8')
        if data_modify is None:
            return None
        return self.f_object.decrypt(data_modify).decode('utf-8')
