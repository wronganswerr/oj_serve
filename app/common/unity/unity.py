import time
import hashlib
import uuid


def get_hash_id(be_recoed):
    now_timestamps = int(time.time()) # second
    h1 = hashlib.md5()
    be_recoed = str(now_timestamps) + be_recoed
    h1.update(be_recoed.encode('utf-8'))
    return h1.hexdigest()

async def get_search_id(user_id):
    # make hashed_user_id by using MD5
    hashed_user_id = hashlib.md5(str(user_id).encode()).hexdigest()

    # gerenate a random UUID without dashes
    uuid_part = uuid.uuid4().hex

    # combine the two parts
    combined = hashed_user_id + uuid_part

    # gerenate a search_id by using MD5
    return hashlib.md5(combined.encode()).hexdigest()