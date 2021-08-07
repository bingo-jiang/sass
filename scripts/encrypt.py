import hashlib
from django.conf import settings
import uuid


def data_encryption(data):
    obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    # obj = hashlib.md5()
    obj.update(data.encode('utf-8'))
    return obj.hexdigest()


def uid(string):
    data = "{}-{}".format(uuid.uuid4(), string)
    data = data_encryption(data)
    return data


if __name__ == '__main__':
    string = '123456'
    res = data_encryption(string)
    new = data_encryption(res)
    print(res)
    print(new)
