import math
import types

from .rules import rules_chain
from .supports import raw_object, typed_object, function, _dump_obj, raw_type
from ..utils import dynamic_call


@dynamic_call
def builtin_int(v: int, addon):
    addon.is_type(v, int)
    return repr(v)


@dynamic_call
def builtin_float(v: float, addon):
    addon.is_type(v, float)
    with addon.transaction():
        if math.isinf(v):
            return ('+' if v > 0 else '-') + addon.obj_attr(math, 'inf')
        elif math.isnan(v):
            return addon.obj_attr(math, 'nan')
        else:
            if math.isclose(v, math.e):
                return addon.obj_attr(math, 'e')
            elif math.isclose(v, math.pi):
                return addon.obj_attr(math, 'pi')
            elif math.isclose(v, math.tau):
                return addon.obj_attr(math, 'tau')
            else:
                return repr(v)


@dynamic_call
def builtin_str(v: str, addon):
    addon.is_type(v, str)
    return repr(v)


@dynamic_call
def builtin_none(v: None, addon):
    if v is not None:
        addon.unprocessable()
    return repr(v)


@dynamic_call
def builtin_list(v: list, addon):
    addon.is_type(v, list)
    with addon.transaction():
        if type(v) == list:
            return f'[{", ".join(map(addon.rule, v))}]'
        else:
            return addon.func_call(type(v), list(v))


@dynamic_call
def builtin_tuple(v: tuple, addon):
    addon.is_type(v, tuple)
    with addon.transaction():
        if type(v) == tuple:
            return f'({", ".join(map(addon.rule, v))}{", " if len(v) == 1 else ""})'
        else:
            return addon.func_call(type(v), tuple(v))


@dynamic_call
def builtin_set(v: set, addon):
    addon.is_type(v, set)
    with addon.transaction():
        if type(v) == set:
            if len(v) > 0:
                return f'{{{", ".join(map(addon.rule, v))}}}'
            else:
                return 'set()'
        else:
            return addon.func_call(type(v), set(v))


@dynamic_call
def builtin_dict(v: dict, addon):
    addon.is_type(v, dict)
    with addon.transaction():
        if type(v) == dict:
            return f'{{{", ".join(map(lambda e: f"{addon.rule(e[0])}: {addon.rule(e[1])}", v.items()))}}}'
        else:
            return addon.func_call(type(v), dict(v))


@dynamic_call
def builtin_bytes(v: bytes, addon):
    addon.is_type(v, bytes)
    return repr(v)


@dynamic_call
def builtin_bytearray(v: bytearray, addon):
    addon.is_type(v, bytearray)
    with addon.transaction():
        return addon.func_call(bytearray, bytes(v))


@dynamic_call
def builtin_func(v, addon):
    addon.is_type(v, types.FunctionType)
    with addon.transaction():
        return addon.func_call(function, _dump_obj(v))


@dynamic_call
def builtin_type(v: type, addon):
    addon.is_type(v, type)
    with addon.transaction():
        try:
            _import = addon.quick_import(v)
        except (ImportError, TypeError):
            _full_name = ((v.__module__ + '.') if hasattr(v, '__module__') else '') + v.__name__
            return addon.func_call(raw_type, _full_name, _dump_obj(v))
        else:
            return _import.target


@dynamic_call
def any_(v, addon):
    with addon.transaction():
        try:
            _i = addon.quick_import(type(v))
        except (ImportError, TypeError):
            return addon.func_call(raw_object, _dump_obj(v))
        else:
            return addon.func_call(typed_object, type(v), _dump_obj(v))


builtins_ = rules_chain(
    builtin_int,
    builtin_float,
    builtin_str,
    builtin_none,
    builtin_list,
    builtin_tuple,
    builtin_set,
    builtin_dict,
    builtin_bytes,
    builtin_bytearray,
    builtin_func,
    builtin_type,
    any_,
)
