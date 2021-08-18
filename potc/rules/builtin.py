import builtins
import math
import types

from ..fixture import Addons, rule
from ..supports import raw_object, typed_object, function, raw_type
from ..supports.bin import dump_obj


@rule(type_=type(...))
def builtin_ellipsis():
    return '...'


@rule(type_=int)
def builtin_int(v: int):
    return repr(v)


@rule(type_=float)
def builtin_float(v: float, addon: Addons):
    if math.isinf(v):
        return ('+' if v > 0 else '-') + str(addon.obj(math).inf)
    elif math.isnan(v):
        return addon.obj(math).nan
    else:
        if math.isclose(v, math.e):
            return addon.obj(math).e
        elif math.isclose(v, math.pi):
            return addon.obj(math).pi
        elif math.isclose(v, math.tau):
            return addon.obj(math).tau
        else:
            return repr(v)


@rule(type_=str)
def builtin_str(v: str):
    return repr(v)


@rule(type_=type(None))
def builtin_none():
    return 'None'


@rule(type_=range)
def builtin_range(v: range, addon: Addons):
    if v.step == 1:
        if v.start == 0:
            _args = (v.stop,)
        else:
            _args = (v.start, v.stop,)
    else:
        _args = (v.start, v.stop, v.step)
    return addon.val(range)(*_args)


@rule(type_=slice)
def builtin_slice(v: slice, addon: Addons):
    if v.step is None:
        if v.start is None:
            _args = (v.stop,)
        else:
            _args = (v.start, v.stop)
    else:
        _args = (v.start, v.stop, v.step)
    return addon.val(slice)(v.start, v.stop, v.step)


@rule(type_=list)
def builtin_list(v: list, addon: Addons):
    if type(v) == list:
        return f'[{", ".join(map(addon.rule, v))}]'
    else:
        return addon.obj(type(v))(list(v))


@rule(type_=tuple)
def builtin_tuple(v: tuple, addon: Addons):
    if type(v) == tuple:
        return f'({", ".join(map(addon.rule, v))}{", " if len(v) == 1 else ""})'
    else:
        return addon.obj(type(v))(tuple(v))


@rule(type_=(set, frozenset))
def builtin_set(v: set, addon: Addons):
    if type(v) == set:
        if len(v) > 0:
            return f'{{{", ".join(map(addon.rule, v))}}}'
        else:
            return 'set()'
    else:
        return addon.obj(type(v))(set(v))


@rule(type_=dict)
def builtin_dict(v: dict, addon: Addons):
    if type(v) == dict:
        return f'{{{", ".join(map(lambda e: f"{addon.rule(e[0])}: {addon.rule(e[1])}", v.items()))}}}'
    else:
        return addon.obj(type(v))(dict(v))


@rule(type_=(bytes, bytearray, memoryview))
def builtin_bytes(v: bytes, addon: Addons):
    if type(v) == bytes:
        return repr(v)
    else:
        return addon.val(type(v))(bytes(v))


_BUILTIN_ITEMS_NAMES = {id(value): key for key, value in builtins.__dict__.items() if not isinstance(value, type)}


@rule()
def builtin_items(v, addon: Addons):
    if id(v) in _BUILTIN_ITEMS_NAMES.keys():
        return _BUILTIN_ITEMS_NAMES[id(v)]
    else:
        addon.unprocessable()


# noinspection PyTypeChecker
@rule(type_=types.FunctionType)
def builtin_func(v, addon: Addons):
    return addon.obj(function)(v.__name__, dump_obj(v))


_TYPES_TYPE_NAMES = {getattr(types, name): name for name in filter(lambda x: x.endswith('Type'), dir(types))}
_BUILTIN_TYPE_NAMES = {value: key for key, value in builtins.__dict__.items() if isinstance(value, type)}


@rule(type_=type)
def builtin_type(v: type, addon: Addons):
    try:
        if v in _BUILTIN_TYPE_NAMES.keys():
            return _BUILTIN_TYPE_NAMES[v]
        elif v in _TYPES_TYPE_NAMES.keys():
            return getattr(addon.obj(types), _TYPES_TYPE_NAMES[v])
        else:
            return addon.obj(v)
    except (ImportError, TypeError):
        _full_name = ((v.__module__ + '.') if hasattr(v, '__module__') else '') + v.__name__
        return addon.obj(raw_type)(_full_name, dump_obj(v))


@rule(type_=types.ModuleType)
def builtin_module(v, addon: Addons):
    return addon.obj(v)


@rule()
def builtin_object(v, addon: Addons):
    try:
        _i = addon.obj(type(v))
    except (ImportError, TypeError):
        return addon.obj(raw_object)(dump_obj(v))
    else:
        return addon.obj(typed_object)(type(v), dump_obj(v))


builtin_basic = (
    builtin_int,
    builtin_float,
    builtin_str,
    builtin_none,
    builtin_range,
    builtin_slice,
    builtin_ellipsis,
    builtin_bytes,
)
builtin_collection = (
    builtin_list,
    builtin_tuple,
    builtin_set,
    builtin_dict,
)
builtin_reflect = (
    builtin_items,
    builtin_func,
    builtin_type,
    builtin_module,
)
builtin_all = [
    (
        builtin_basic,
        builtin_collection,
        builtin_reflect,
        builtin_object,
    ),
]