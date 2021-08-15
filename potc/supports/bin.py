import zlib

import dill


def dump_obj(obj):
    return zlib.compress(dill.dumps(obj))


def load_obj(data: bytes):
    return dill.loads(zlib.decompress(data))
