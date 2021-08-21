import zlib

import dill


def dump_obj(obj: object) -> bytes:
    """
    Overview:
        Dump any object to binary format.
        In order to reduce the size of bytes as much as possible, \
        zlib compression is applied in this function.

    Arguments:
        - obj (:obj:`object`): Any object.

    Returns:
        - data (:obj:`bytes`): Dumped bytes data.
    """
    return zlib.compress(dill.dumps(obj))


def load_obj(data: bytes) -> object:
    """
    Overview:
        Load any object from binary format.

    Arguments:
        - data (:obj:`bytes`): Dumped bytes data.

    Returns:
        - obj (:obj:`object`): Original object.
    """
    return dill.loads(zlib.decompress(data))
