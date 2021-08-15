from typing import Type, TypeVar, Callable

from .bin import load_obj


def raw_object(data: bytes) -> object:
    return load_obj(data)


def raw_type(name: str, data: bytes) -> type:
    return load_obj(data)


_T = TypeVar('_T')


# noinspection PyUnusedLocal
def typed_object(type_: Type[_T], data: bytes) -> _T:
    return load_obj(data)


def function(name: str, data: bytes) -> Callable:
    return load_obj(data)
