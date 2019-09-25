import hashlib
from os import urandom


def _hash_file(f):
    f.seek(0)
    hasher = hashlib.md5()
    block = f.read(65536)
    while len(block) > 0:
        hasher.update(block)
        block = f.read(65536)

    return hasher.hexdigest()


def hash_file(f):
    if isinstance(f, str):
        with open(f, 'rb') as fr:
            return _hash_file(fr)
    else:
        return _hash_file(f)


def rand_str(num=64):
    return urandom(num).hex()
