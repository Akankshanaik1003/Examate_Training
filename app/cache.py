import time

TTL_SECONDS = 3600
_CACHE = {}


def get(key):
    item = _CACHE.get(key)
    if item and time.time() - item[0] < TTL_SECONDS:
        return item[1]
    return None


def put(key, value):
    _CACHE[key] = (time.time(), value)