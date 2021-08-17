import builtins
import math
import types

from ..fixture import Addons, rule
from ..supports import raw_object, typed_object, function, raw_type
from ..supports.bin import dump_obj


@rule()
def builtin_ellipsis(v, addon: Addons):
    addon.is_type(v, type(...))
    return '...'


@rule()
def builtin_int(v: int, addon: Addons):
    addon.is_type(v, int)
    return repr(v)


@rule()
def builtin_float(v: float, addon: Addons):
    addon.is_type(v, float)
    with addon.transaction():
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


@rule()
def builtin_str(v: str, addon: Addons):
    addon.is_type(v, str)
    return repr(v)


@rule()
def builtin_none(v: None, addon: Addons):
    if v is not None:
        addon.unprocessable()
    return repr(v)


@rule()
def builtin_range(v: range, addon: Addons):
    addon.is_type(v, range)
    with addon.transaction():
        return addon.val(range)(v.start, v.stop, v.step)


@rule()
def builtin_slice(v: slice, addon: Addons):
    addon.is_type(v, slice)
    with addon.transaction():
        return addon.val(slice)(v.start, v.stop, v.step)


@rule()
def builtin_list(v: list, addon: Addons):
    addon.is_type(v, list)
    with addon.transaction():
        if type(v) == list:
            return f'[{", ".join(map(addon.rule, v))}]'
        else:
            return addon.obj(type(v))(list(v))


@rule()
def builtin_tuple(v: tuple, addon: Addons):
    addon.is_type(v, tuple)
    with addon.transaction():
        if type(v) == tuple:
            return f'({", ".join(map(addon.rule, v))}{", " if len(v) == 1 else ""})'
        else:
            return addon.obj(type(v))(tuple(v))


@rule()
def builtin_set(v: set, addon: Addons):
    addon.is_type(v, set)
    with addon.transaction():
        if type(v) == set:
            if len(v) > 0:
                return f'{{{", ".join(map(addon.rule, v))}}}'
            else:
                return 'set()'
        else:
            return addon.obj(type(v))(set(v))


@rule()
def builtin_dict(v: dict, addon: Addons):
    addon.is_type(v, dict)
    with addon.transaction():
        if type(v) == dict:
            return f'{{{", ".join(map(lambda e: f"{addon.rule(e[0])}: {addon.rule(e[1])}", v.items()))}}}'
        else:
            return addon.obj(type(v))(dict(v))


@rule()
def builtin_bytes(v: bytes, addon: Addons):
    addon.is_type(v, bytes)
    return repr(v)


@rule()
def builtin_bytearray(v: bytearray, addon: Addons):
    addon.is_type(v, bytearray)
    with addon.transaction():
        return addon.val(bytearray)(bytes(v))


@rule()
def builtin_func(v, addon: Addons):
    addon.is_type(v, types.FunctionType)
    with addon.transaction():
        return addon.obj(function)(v.__name__, dump_obj(v))


_TYPES_TYPE_NAMES = {getattr(types, name): name for name in filter(lambda x: x.endswith('Type'), dir(types))}
_BUILTIN_TYPE_NAMES = {value: key for key, value in builtins.__dict__.items() if isinstance(value, type)}


@rule()
def builtin_type(v: type, addon: Addons):
    addon.is_type(v, type)
    with addon.transaction():
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


@rule()
def builtin_module(v, addon: Addons):
    addon.is_type(v, types.ModuleType)
    with addon.transaction():
        return addon.obj(v)


@rule()
def builtin_object(v, addon: Addons):
    with addon.transaction():
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
    builtin_bytearray,
)
builtin_collection = (
    builtin_list,
    builtin_tuple,
    builtin_set,
    builtin_dict,
)
builtin_reflect = (
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
