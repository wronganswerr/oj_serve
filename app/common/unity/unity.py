import time
import hashlib


def get_hash_id(be_recoed):
    now_timestamps = int(time.time()) # second
    h1 = hashlib.md5()
    be_recoed = str(now_timestamps) + be_recoed
    h1.update(be_recoed.encode('utf-8'))
    return h1.hexdigest()