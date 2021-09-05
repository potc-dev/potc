from typing import Type, TypeVar

from .bin import load_obj


def raw_object(data: bytes) -> object:
    """
    Overview:
        Raw object function support.

    Arguments:
        - data (:obj:`bytes`): Binary data.

    Returns:
        - obj (:obj:`object`): Loaded object,
    """
    return load_obj(data)


def raw_type(name: str, data: bytes) -> type:
    """
    Overview:
        Raw type function support.

    Arguments:
        - name (:obj:`str`): Name of the type.
        - data (:obj:`bytes`): Binary data.

    Returns:
        - type\_ (:obj:`object`): Loaded type,
    """
    return load_obj(data)


_T = TypeVar('_T')


# noinspection PyUnusedLocal
def typed_object(type_: Type[_T], data: bytes) -> _T:
    """
    Overview:
        Typed object function support.

    Arguments:
        - type\_ (:obj:`Type[_T]`): Type of the object.
        - data (:obj:`bytes`): Binary data.

    Returns:
        - obj (:obj:`_T`): Loaded typed object,
    """
    return load_obj(data)


def function(name: str, scheme, data: bytes):
    """
    Overview:
        Function function support.

    Arguments:
        - name (:obj:`str`): Name of the function.
        - scheme (:obj:`Type[Callable]`): Scheme of the function.
        - data (:obj:`bytes`): Binary data.

    Returns:
        - obj (:obj:`Callable`): Loaded function.
    """
    _func: scheme = load_obj(data)
    return _func
