import re
import typing

try:
    from collections.abc import Callable as _CollectionCallable
except ImportError:
    _CollectionCallable = None
from collections import OrderedDict
from functools import lru_cache, wraps
from types import FunctionType
from typing import TypeVar, Callable

from .builtin import builtin_type, builtin_raw_type
from ...fixture import rule, Addons

try:
    from types import GenericAlias
except ImportError:
    GenericAlias = None


@lru_cache()
def _get_origin_trans_map():
    return {
        value.__origin__: value
        for key, value in typing.__dict__.items()
        if getattr(value, '__origin__', None) and isinstance(value.__origin__, type)
    }


def _origin_trans(v):
    o = v.__origin__
    if GenericAlias is not None and isinstance(v, GenericAlias):
        return o
    else:
        return _get_origin_trans_map().get(o, o)


def _is_wrapper(func):
    @wraps(func)
    def _new_func(v, addon: Addons):
        if hasattr(v, '__origin__') and hasattr(v, '__args__'):
            return func(v, addon)
        else:
            addon.unprocessable()

    return _new_func


@rule()
@_is_wrapper
def typing_callable(v, addon: Addons):
    if (_CollectionCallable is not None and v.__origin__ == _CollectionCallable) or \
            (Callable is not None and v.__origin__ == Callable):
        _base = addon.val(_origin_trans(v))
        _args, _ret = v.__args__[:-1], v.__args__[-1]
        if _args == (Ellipsis,):
            return _base[v.__args__]
        else:
            return _base[list(_args), _ret]

    else:
        addon.unprocessable()


@rule()
@_is_wrapper
def typing_wrapper(v, addon: Addons):
    _base = addon.val(_origin_trans(v))
    if len(v.__args__) == 0:
        return _base
    elif len(v.__args__) == 1:
        return _base[v.__args__[0]]
    else:
        return _base[v.__args__]


_common_types = (type, FunctionType)
try:
    from typing import TypingMeta


    def _is_item(x):
        return isinstance(x, _common_types) or isinstance(type(x), TypingMeta)

except ImportError:
    from typing import _Final


    def _is_item(x):
        return isinstance(x, (*_common_types, _Final))

_ALL_NAMES = set(typing.__all__)
_STD_NAME = re.compile('^[A-Z][A-Za-z0-9]*$')


def _is_name(k):
    return k in _ALL_NAMES or _STD_NAME.fullmatch(k)


_TYPING_ITEMS = {value: key for key, value in typing.__dict__.items() if _is_name(key) and _is_item(value)}


@rule()
def typing_items(v, addon: Addons):
    if _is_item(v) and v in _TYPING_ITEMS.keys():
        _v_name = _TYPING_ITEMS[v]
        try:
            return addon.obj(v, _v_name)
        except (ImportError, TypeError):
            addon.from_(typing.__name__).import_(_v_name)
            return addon.raw(_v_name)
    else:
        addon.unprocessable()


@rule(type_=TypeVar)
def typing_typevar(v: TypeVar, addon: Addons):
    _kwargs = OrderedDict()
    if v.__bound__ is not None:
        _kwargs['bound'] = v.__bound__
    if v.__covariant__:
        _kwargs['covariant'] = v.__covariant__
    if v.__contravariant__:
        _kwargs['contravariant'] = v.__contravariant__

    return addon.obj(TypeVar)(v.__name__, *v.__constraints__, **_kwargs)


_typing_self_all = [
    (
        typing_typevar,
        typing_items,
        typing_callable,
        typing_wrapper,
    )
]

#: Overview:
#:      Typing types
#:
#: Items:
#:      - :class:`TypeVar`
#:      - Items in module ``typing``
#:      - :class:`Callable`
#:      - :class:`Wrapper`
typing_all = [
    (builtin_type, _typing_self_all, builtin_raw_type),
]
