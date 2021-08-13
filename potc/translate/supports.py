import zlib
from typing import Type, TypeVar, Callable

import dill


def _dump_obj(obj):
    return zlib.compress(dill.dumps(obj))


def _load_obj(data: bytes):
    return dill.loads(zlib.decompress(data))


def raw_object(data: bytes) -> object:
    return _load_obj(data)


def raw_type(name: str, data: bytes) -> type:
    return _load_obj(data)


_T = TypeVar('_T')


# noinspection PyUnusedLocal
def typed_object(type_: Type[_T], data: bytes) -> _T:
    return _load_obj(data)


def function(name: str, data: bytes) -> Callable:
    return _load_obj(data)
