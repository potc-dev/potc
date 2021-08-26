import re
import typing
from functools import lru_cache
from types import FunctionType

from .builtin import builtin_type, builtin_raw_type
from ...fixture import rule, Addons

try:
    _ = getattr([], '__class_getitem__')
except AttributeError:
    _need_origin_trans = True
else:
    _need_origin_trans = False


@lru_cache()
def _get_origin_trans_map():
    return {
        value.__origin__: value
        for key, value in typing.__dict__.items()
        if getattr(value, '__origin__', None) and isinstance(value.__origin__, type)
    }


def _origin_trans(o):
    if not _need_origin_trans:
        return o
    else:
        return _get_origin_trans_map().get(o, o)


@rule()
def typing_wrapper(v, addon: Addons):
    if hasattr(v, '__origin__') and hasattr(v, '__args__'):
        _base = addon.val(_origin_trans(v.__origin__))
        if len(v.__args__) == 0:
            return _base
        elif len(v.__args__) == 1:
            return _base[v.__args__[0]]
        else:
            return _base[v.__args__]
    else:
        addon.unprocessable()


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


_typing_self_all = [
    (
        typing_items,
        typing_wrapper,
    )
]

typing_all = [
    (builtin_type, _typing_self_all, builtin_raw_type),
]
